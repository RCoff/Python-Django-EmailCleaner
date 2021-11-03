import logging
from pathlib import Path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)
logging.getLogger('googleapiclient').setLevel(logging.INFO)


def auth_google(scopes: list or None = None):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    if scopes is None:
        scopes = ['https://www.googleapis.com/auth/gmail.readonly']

    logger.debug(f"Authenticating with Google API", extra={'scopes': scopes,
                                                           'provider': 'gmail'})
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if Path('token.json').exists():
        logger.debug("Using file 'token.json' for authentication")
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.debug("Refreshing credentials", extra={'scopes': scopes,
                                                          'providor': 'gmail'})
            creds.refresh(Request())
        else:
            logger.debug("Using client secret file 'credentials.json' for authentication")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        logger.debug("Saving credentials to 'token.json'")
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    logger.debug("Done running authentication flow")

    return build('gmail', 'v1', credentials=creds)
