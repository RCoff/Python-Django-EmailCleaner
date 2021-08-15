import logging

import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


def main():
    service_client = auth_google()
    messages = get_unread_emails(userid='me', service_client=service_client)

    print("pause")


def auth_google():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def get_unread_emails(userid, service_client,
                      include_spam_trash: bool = False,
                      max_results: int = 500) -> list:
    messages = service_client.users().messages().list(userId='me', includeSpamTrash=include_spam_trash,
                                                      maxResults=max_results, q="is:unread")
    messages = messages.execute()
    message_id_list = messages['messages']

    if 'nextPageToken' in messages:
        continue_paging = True

        while continue_paging:
            messages = service_client.users().messages().list(userId='me', includeSpamTrash=include_spam_trash,
                                                              maxResults=max_results, q="is:unread", pageToken=messages['nextPageToken'])
            messages = messages.execute()

            if messages['messages']:
                message_id_list = message_id_list + messages['messages']
            if 'nextPageToken' not in messages:
                continue_paging = False

    message_id_list = list(set(message_id_list))

    return message_id_list




if __name__ == "__main__":
    main()
