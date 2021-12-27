import datetime
import logging

import pandas as pd
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from gmail_clean.utils import load_pickle, save_pickle
from gmail_clean.gmail.get_emails import get_emails
from gmail_clean.gmail.parse_emails import parse_emails

logger = logging.getLogger(__name__)


def main(session=None) -> dict:
    creds = Credentials(**session['credentials'])
    service_client = build('gmail', 'v1', credentials=creds)
    # service_client = auth_google(session=session)

    messages = load_pickle('parsed_emails.p')

    if messages is None:
        messages = load_pickle('raw_emails.p')

        if messages is None:
            start_time = datetime.datetime.now()
            messages = get_emails(user_id='me', service_client=service_client, status='all', include_trash=True)
            print((datetime.datetime.now() - start_time) / 60)
            save_pickle(messages, 'raw_emails.p')

        logger.info("Parsing raw emails")
        start_time = datetime.datetime.now()
        messages = parse_emails(messages, service_client)
        print((datetime.datetime.now() - start_time) / 60)
        save_pickle(messages, 'parsed_emails.p')

    df = pd.DataFrame(messages)
    # group_count_df = df.groupby(by=['from-domain'])['id'].count()
    unread_percent_df = pd.pivot_table(df[['domain', 'status']], index='domain', columns='status', aggfunc=len,
                                       fill_value=0)
    unread_percent_df['Unread_%'] = 1 - (
            unread_percent_df['read'] / (unread_percent_df['unread'] + unread_percent_df['read']))
    unread_percent_df = unread_percent_df.sort_values(by=['unread', 'Unread_%'], ascending=False)
    unread_percent_df = unread_percent_df[(unread_percent_df['unread'] >= 10) & (unread_percent_df['Unread_%'] >= 0.75)]

    return {'parsed_messages': df,
            'critical_unread_messages': unread_percent_df,
            'total_messages': len(df.index)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        handlers=[logging.FileHandler('log.log'),
                                  logging.StreamHandler()])
    main()
