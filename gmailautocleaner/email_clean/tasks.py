from data.models import EmailStorage
from celery import shared_task

from .gmail.parse_emails import get_all_messages


@shared_task
def parse_gmail(id_: str, messages: list, service_client):
    pass
