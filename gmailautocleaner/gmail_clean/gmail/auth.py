import logging
from pathlib import Path
import json
import os

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)
logging.getLogger('googleapiclient').setLevel(logging.INFO)


def auth_google(scopes: list or None = None, session=None):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    if scopes is None:
        scopes = ['https://www.googleapis.com/auth/gmail.readonly']

    logger.debug(f"Authenticating with Google API", extra={'scopes': scopes,
                                                           'provider': 'gmail'})
    creds = None
    if session:
        if session.get('credentials'):
            creds = Credentials.from_authorized_user_info(json.loads(session.get('credentials')))

    if not creds or not creds.valid:
        if not creds:
            if Path(__file__).parent.joinpath('token.json').exists():
                logger.debug("Using file 'token.json' for authentication")
                creds = Credentials.from_authorized_user_file('token.json', scopes)

        if creds and creds.expired and creds.refresh_token:
            logger.debug("Refreshing credentials", extra={'scopes': scopes,
                                                          'provider': 'gmail'})
            creds.refresh(Request())
        else:
            logger.debug("Using client secret file 'credentials.json' for authentication")
            if Path(__file__).parent.joinpath('credentials.json').exists():
                creds_file = str(Path(__file__).parent.joinpath('credentials.json').resolve())
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_file, scopes)
                creds = flow.run_local_server(port=0)
            elif os.environ.get('credentials'):
                creds_file = json.loads(os.environ.get('credentials'))
                flow = Flow.from_client_config(client_config=creds_file, scopes=scopes)
                print("pause")
            else:
                raise ValueError('App credentials not provided')

        # Save the credentials for the next run
        session['credentials'] = creds.to_json()
        # logger.debug("Saving credentials to 'token.json'")
        # with open('token.json', 'w') as token:
        #     token.write(creds.to_json())

    logger.debug("Done running authentication flow")

    return build('gmail', 'v1', credentials=creds)
