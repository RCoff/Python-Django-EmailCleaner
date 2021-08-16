import logging
import re
import pickle
import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pandas as pd

import config


def main():
    service_client = auth_google()
    messages = None

    try:
        with open('data.p', 'rb') as pf:
            messages = pickle.load(pf)
    except:
        pass

    if messages is None:
        messages = get_unread_emails(userid='me', service_client=service_client)
        messages = parse_emails(messages, service_client)
        with open('data.p', 'wb') as pf:
            pickle.dump(messages, pf, protocol=pickle.HIGHEST_PROTOCOL)

    df = pd.DataFrame(messages)

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

    return message_id_list


def parse_emails(messages: list, service_client) -> list:
    message_details_list = []
    for message in messages:
        message_details = service_client.users().messages().get(userId='me', id=message['id'], format='full')
        message_details = message_details.execute()

        message_detail_dict = {}
        if 'payload' in message_details:
            message_detail_dict.update({'id': message_details['id']})

            if 'labelIds' in message_details:
                for label in message_details['labelIds']:
                    if label != 'UNREAD' and label != 'INBOX':
                        if label == "IMPORTANT":
                            message_detail_dict.update({'important': True})

                        if 'labels' in message_detail_dict:
                            message_detail_dict.get('labels').append(label)
                        else:
                            message_detail_dict.update({'labels': [label]})

            if 'headers' in message_details['payload']:
                if len(message_details['payload']['headers']) > 0:
                    for header in message_details['payload']['headers']:
                        if header.get('name', None) == 'From':
                            message_detail_dict.update({'from': header.get('value', "")})
                            message_detail_dict.update({'from-domain': parse_email_domain(header.get('value', ""))})
                        elif header.get('name', None) == 'Subject':
                            message_detail_dict.update({'subject': header.get('value', "")})
                        elif header.get('name', None) == 'List-Unsubscribe-Post':
                            message_detail_dict.update({'unsubscribe-type': header.get('value', "")})
                        elif header.get('name', None) == 'List-Unsubscribe':
                            message_detail_dict.update({'unsubscribe': header.get('value', "")})
                    else:
                        message_details_list.append(message_detail_dict)

    return message_details_list


def parse_email_domain(sender_email: str):
    regex_string = r"(?<=@).*\.[a-zA-Z]{2,3}(?=\>|$)"
    parsed_sender = re.search(regex_string, sender_email).group(0)

    return parsed_sender


if __name__ == "__main__":
    main()
