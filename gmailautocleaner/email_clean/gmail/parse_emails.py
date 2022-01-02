import logging
from email_clean.utils import parse_email_domain

logger = logging.getLogger(__name__)


def parse_emails(messages: list, service_client) -> list:
    """

    :param messages:
    :param service_client:
    :return:
    """

    message_details_list = []
    for message in messages:
        message_details = service_client.users().messages().get(userId='me',
                                                                id=message['id'],
                                                                format='metadata').execute()

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

    return message_details_list
