import datetime
import logging
import time

from email_clean.utils import parse_email_domain
from email_clean.exceptions import *

logger = logging.getLogger(__name__)


def _get_all_messages(messages: list, service_client) -> tuple:
    message_detail_list = []

    def _callback_get_all_messages(request_id, response, exception):
        if exception:
            if exception.status_code == 403:
                raise QuotaLimitReached
            else:
                raise ValueError(exception)
        else:
            return message_detail_list.append(response)

    chunk_size = 100
    for chunk in range(0, len(messages), chunk_size):
        message_batch = service_client.new_batch_http_request(callback=_callback_get_all_messages)
        messages_chunk = messages[chunk: chunk + chunk_size]
        for message in messages_chunk:
            message_batch.add(service_client.users().messages().get(userId='me',
                                                                    id=message['id'],
                                                                    format='metadata'))
        for retry in range(3):
            try:
                message_batch.execute()
                break
            except QuotaLimitReached:  # If quota limit is reached, wait and retry the batch
                print(f"Retrying... {retry + 1}")  # TODO: Replace with logging
                time.sleep(30 + (retry * 20))
                continue

    return tuple(message_detail_list)


def parse_emails(messages: list, service_client) -> list:
    """

    :param messages:
    :param service_client:
    :return:
    """

    message_details_list = []

    start_time = datetime.datetime.now()
    message_response_tuple = _get_all_messages(messages, service_client)
    print(f"Time to retrieve messages: {datetime.datetime.now() - start_time}")

    start_time = datetime.datetime.now()
    for message_details in message_response_tuple:
        message_detail_dict = {'id': message_details['id']}

        if 'headers' in message_details['payload']:
            headers = message_details['payload']['headers']

            for header in headers:
                if header.get('name', None) == 'From':
                    message_detail_dict.update({'from': header.get('value', "")})
                    from_domain = parse_email_domain(header.get('value', ""))
                    message_detail_dict.update({'from-domain': from_domain})
                    if from_domain.count('.') > 1:
                        message_detail_dict.update({'domain': from_domain[from_domain.find('.', ) + 1:]})
                    elif from_domain.count('.') == 1:
                        message_detail_dict.update({'domain': from_domain})
                elif header.get('name') == 'Date':
                    message_detail_dict.update({'date-received': header.get('value', "")})
                elif header.get('name', None) == 'Subject':
                    message_detail_dict.update({'subject': header.get('value', "")})
                elif header.get('name', None) == 'List-Unsubscribe-Post':
                    message_detail_dict.update({'unsubscribe-type': header.get('value', "")})
                elif header.get('name', None) == 'List-Unsubscribe':
                    message_detail_dict.update({'unsubscribe': header.get('value', "")})
            else:
                if not message_detail_dict.get('unsubscribe'):
                    message_detail_dict.update({'unsubscribe': ""})

                message_details_list.append(message_detail_dict)

        if 'labelIds' in message_details:
            labels = message_details['labelIds']
            message_detail_dict.update({'labels': labels})

            if 'UNREAD' in labels:
                message_detail_dict.update({'status': 'unread'})
            else:
                message_detail_dict.update({'status': 'read'})

            message_detail_dict.update({'is_trash': 'TRASH' in labels})
            message_detail_dict.update({'is_spam': 'SPAM' in labels})
            message_detail_dict.update({'important': 'IMPORTANT' in labels})

    logging.debug(f"{len(message_details_list)} emails parsed")

    print(f"Time to parse: {datetime.datetime.now() - start_time}")
    return message_details_list
