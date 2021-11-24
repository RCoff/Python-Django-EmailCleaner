import logging
from pathlib import Path
import json
import os

from django.shortcuts import HttpResponseRedirect, reverse
from google_auth_oauthlib.flow import Flow

logger = logging.getLogger(__name__)
logging.getLogger('googleapiclient').setLevel(logging.INFO)


# TODO: https://developers.google.com/identity/protocols/oauth2/web-server

def gmail_sign_in(request):
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


# def auth_google(scopes: list or None = None, session=None):
#     """Shows basic usage of the Gmail API.
#     Lists the user's Gmail labels.
#     """
#     if scopes is None:
#         scopes = ['https://www.googleapis.com/auth/gmail.readonly']
#
#     logger.debug(f"Authenticating with Google API", extra={'scopes': scopes,
#                                                            'provider': 'gmail'})
#     creds = None
#     if session:
#         if session.get('credentials'):
#             creds = Credentials.from_authorized_user_info(json.loads(session.get('credentials')))
#
#     if not creds or not creds.valid:
#         if not creds:
#             if Path(__file__).parent.joinpath('token.json').exists():
#                 logger.debug("Using file 'token.json' for authentication")
#                 creds = Credentials.from_authorized_user_file('token.json', scopes)
#
#         if creds and creds.expired and creds.refresh_token:
#             logger.debug("Refreshing credentials", extra={'scopes': scopes,
#                                                           'provider': 'gmail'})
#             creds.refresh(Request())
#         else:
#             logger.debug("Using client secret file 'credentials.json' for authentication")
#             if Path(__file__).parent.joinpath('credentials_.json').exists():
#                 creds_file = str(Path(__file__).parent.joinpath('credentials.json').resolve())
#                 flow = InstalledAppFlow.from_client_secrets_file(
#                     creds_file, scopes)
#                 creds = flow.run_local_server(port=0)
#             else:
#                 if os.environ.get('credentials'):
#                     creds_file = json.loads(os.environ.get('credentials'))
#                 elif os.environ.get('web_credentials'):
#                     creds_file = json.loads(os.environ.get('web_credentials'))
#                 else:
#                     raise ValueError('App credentials not provided')
#
#                 flow = Flow.from_client_config(client_config=creds_file, scopes=scopes)
#                 flow.redirect_uri = os.environ.get('google_redirect_uri')
#                 authorization_url, state = flow.authorization_url(
#                     access_type='offline',
#                     include_granted_scopes='true'
#                 )
#                 print("pause")
#
#             # Save the credentials for the next run
#             session['credentials'] = creds.to_json()
#             # logger.debug("Saving credentials to 'token.json'")
#             # with open('token.json', 'w') as token:
#             #     token.write(creds.to_json())
#
#     logger.debug("Done running authentication flow")
#
#     return build('gmail', 'v1', credentials=creds)
