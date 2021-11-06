from django.shortcuts import HttpResponseRedirect, reverse
from .auth import outlook_sign_in, get_token_from_code
import requests


def get_emails(request):
    endpoint_url = "https://graph.microsoft.com/v1.0/me/messages"
    token = get_token_from_code(request)['access_token']

    headers = {'Authorization': f'Bearer {token}'}

    raw_messages = []
    messages_resp = requests.get(endpoint_url, headers=headers).json()
    if messages_resp.get('value'):
        raw_messages = raw_messages + messages_resp['value']

    while messages_resp.get('@odata.nextLink'):
        messages_resp = requests.get(messages_resp['@odata.nextLink'], headers=headers).json()
        if messages_resp.get('value'):
            raw_messages = raw_messages + messages_resp['value']

    print("pause")

    return raw_messages
