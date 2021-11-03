import logging


def get_emails(service_client,
               user_id: str = 'me',
               include_spam_trash: bool = False,
               include_trash: bool = True,
               max_results: int = 500,
               status: str = 'unread') -> list:
    if str(status).upper() == 'UNREAD' or status is None:
        query = "is:unread"
    elif str(status).upper() == 'READ':
        query = "is:read"
    elif str(status).upper() == 'ALL':
        query = None
    else:
        raise ValueError("Parameter 'status' must be one of: unread, read, all")

    if include_trash is True:
        in_trash = "in:trash"
        if query is None:
            query = in_trash
        else:
            query = query + f" {in_trash}"

    messages = service_client.users().messages().list(userId=user_id,
                                                      includeSpamTrash=include_spam_trash,
                                                      maxResults=max_results,
                                                      q=query).execute()
    message_id_list = messages['messages']

    if 'nextPageToken' in messages:
        continue_paging = True

        while continue_paging:
            messages = service_client.users().messages().list(userId=user_id,
                                                              includeSpamTrash=include_spam_trash,
                                                              maxResults=max_results,
                                                              q=query,
                                                              pageToken=messages['nextPageToken']).execute()
            if messages['messages']:
                message_id_list = message_id_list + messages['messages']
            if 'nextPageToken' not in messages:
                continue_paging = False

    logging.debug(f"{len(message_id_list)} messages retrieved")

    return message_id_list
