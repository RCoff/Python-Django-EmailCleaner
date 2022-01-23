import logging
from pathlib import Path
import json
import os

from django.contrib.auth.models import User
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from django.shortcuts import redirect, reverse
from google_auth_oauthlib.flow import Flow
from django.contrib.auth import login

logger = logging.getLogger(__name__)
logging.getLogger('googleapiclient').setLevel(logging.INFO)


def gmail_sign_in(request):
    auth_url, state = get_sign_in_flow()
    request.session['state'] = state

    return redirect(auth_url)


def gmail_callback(request):
    credentials = get_token_from_code(request)
    request.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    user = get_or_create_user(request, **request.session['credentials'])
    login(request, user)

    # TODO: Redirect to an error page if something goes wrong

    return redirect(reverse('gmail-load'))


def get_sign_in_flow():
    flow = get_flow()
    flow.redirect_uri = os.environ.get('gmail_redirect_uri')

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    return authorization_url, state


def get_flow(state: str = None):
    return Flow.from_client_config(
        client_config=json.loads(os.environ.get('gmail_client_config')),
        scopes=['https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/userinfo.email'],
        state=state
    )


def get_token_from_code(request):
    flow = get_flow(state=request.session['state'])
    flow.redirect_uri = os.environ.get('gmail_redirect_uri')

    flow.fetch_token(code=request.GET.get('code'))

    credentials = flow.credentials
    return credentials


def get_or_create_user(request, **credentials) -> User or None:
    creds = Credentials(**credentials)

    user_info_service = build('oauth2', 'v2', credentials=creds)
    user_info = user_info_service.userinfo().get().execute()

    user, user_created = User.objects.get_or_create(username=user_info['email'], email=user_info['email'])
    if user_created:
        user.set_unusable_password()
        user.save()

    return user
