import datetime
import logging

from django.shortcuts import reverse, HttpResponse, HttpResponseRedirect
from django.utils import timezone
import googleapiclient.http
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from email_clean.gmail.get_emails import list_emails
from email_clean.tasks import parse_gmail
from data.models import EmailStorage

logger = logging.getLogger(__name__)


def main(request=None):
    creds = Credentials(**request.session['credentials'])

    try:
        user_info_service = build('oauth2', 'v2', credentials=creds)
        user_info = user_info_service.userinfo().get().execute()
    except googleapiclient.http.HttpError:
        del request.session['credentials']
        return HttpResponseRedirect(reverse('gmail-sign-in'))

    service_client = build('gmail', 'v1', credentials=creds)

    email_storage_obj, created = EmailStorage.objects.get_or_create(user_email=user_info['email'])
    if created:
        email_storage_obj.expiration = timezone.now() + datetime.timedelta(hours=24)

    messages = email_storage_obj.parsed_emails
    if messages is None:
        messages = email_storage_obj.raw_emails
        if messages is None:
            start_time = datetime.datetime.now()

            logger.debug(f"Begin getting messages from Gmail API")
            messages = list_emails(user_id='me', service_client=service_client, status='all')
            print(f"Message list retrieval time: {datetime.datetime.now() - start_time}")

            email_storage_obj.raw_emails = messages
            email_storage_obj.parse_status = 'ns'
            email_storage_obj.save()

        task = parse_gmail.delay(request.session['credentials'], email_storage_obj.id)
        print(task.id)

    return HttpResponseRedirect(reverse('gmail-display', args=[email_storage_obj.id]))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        handlers=[logging.FileHandler('log.log'),
                                  logging.StreamHandler()])
    main()
