import logging
import datetime

from celery import shared_task
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from data.models import EmailStorage
from .gmail.parse_emails import parse_emails

logger = logging.getLogger(__name__)


@shared_task
def parse_gmail(credentials: dict, user_obj_id: str):
    creds = Credentials(**credentials)
    service_client = build('gmail', 'v1', credentials=creds)

    logger.info("Parsing raw emails")
    start_time = datetime.datetime.now()
    email_storage_obj = EmailStorage.objects.get(id=user_obj_id)
    messages = email_storage_obj.raw_emails

    email_storage_obj.parsed_status = 'ip'
    email_storage_obj.save()

    logger.debug("Begin parsing messages from GMail")
    messages = parse_emails(messages, service_client)
    email_storage_obj.parsed_emails = messages
    email_storage_obj.parse_status = 'cp'
    email_storage_obj.save()

    print(f"Parse time: {datetime.datetime.now() - start_time}")
