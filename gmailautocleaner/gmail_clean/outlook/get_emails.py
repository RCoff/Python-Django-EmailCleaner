import logging

import requests
from django.shortcuts import HttpResponseRedirect, reverse

from .auth import outlook_sign_in, get_token_from_code
from data.models import EmailStorage
from data.utils import write_messages_to_db

logger = logging.getLogger(__name__)


def get_emails(request):
    endpoint_url = "https://graph.microsoft.com/v1.0/me/messages"
    token = get_token_from_code(request)['access_token']

    headers = {'Authorization': f'Bearer {token}'}
    user_email = _get_user_email(token)

    # if request.session.get('messages_id'):
    #     user_data = EmailStorage.objects.get(id=request.session.get('messages_id'))

    user_data = EmailStorage.objects.filter(user_email=user_email).order_by('-created')
    if len(user_data) > 0:
        raw_messages = user_data[0].messages_json
    else:
        raw_messages = []
        messages_resp = requests.get(endpoint_url, headers=headers).json()
        if messages_resp.get('value'):
            raw_messages = raw_messages + messages_resp['value']

        while messages_resp.get('@odata.nextLink'):
            messages_resp = requests.get(messages_resp['@odata.nextLink'], headers=headers).json()
            if messages_resp.get('value'):
                raw_messages = raw_messages + messages_resp['value']

        print(f"{len(raw_messages)} messages returned")
        new_messages = write_messages_to_db(user_email, {'messages': raw_messages})
        request.session['messages_id'] = new_messages.id

    return raw_messages


def _get_user_email(token: str) -> str:
    headers = {'Authorization': f"Bearer {token}"}
    endpoint_url = "https://graph.microsoft.com/v1.0/me?$select=userPrincipalName,email"

    user_response = requests.get(endpoint_url, headers=headers)
    if user_response.ok:
        user_response = user_response.json()

    if user_response.get('email'):
        return user_response['email']
    elif user_response.get('userPrincipalName'):
        return user_response['userPrincipalName']
    else:
        raise ValueError("User email address not found")
