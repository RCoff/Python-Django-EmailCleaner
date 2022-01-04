import logging
from pathlib import Path
import json
import os

from django.shortcuts import HttpResponseRedirect, reverse
from google_auth_oauthlib.flow import Flow

logger = logging.getLogger(__name__)
logging.getLogger('googleapiclient').setLevel(logging.INFO)


def gmail_sign_in(request):
    if request.session.get('credentials'):
        if request.session['credentials'].get('refresh_token') and \
                request.session['credentials'].get('token_uri') and \
                request.session['credentials'].get('client_id') and \
                request.session['credentials'].get('client_secret'):
            return HttpResponseRedirect(reverse('gmail-load'))

    auth_url, state = get_sign_in_flow()
    request.session['state'] = state

    return HttpResponseRedirect(auth_url)


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

    return HttpResponseRedirect(reverse('gmail-load'))


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
        scopes=['https://www.googleapis.com/auth/gmail.readonly'],
        state=state
    )


def get_token_from_code(request):
    flow = get_flow(state=request.session['state'])
    flow.redirect_uri = os.environ.get('gmail_redirect_uri')

    flow.fetch_token(code=request.GET.get('code'))

    credentials = flow.credentials
    return credentials
