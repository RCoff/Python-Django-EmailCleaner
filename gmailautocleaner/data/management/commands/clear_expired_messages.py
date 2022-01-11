import logging

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from data.models import EmailStorage

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Delete user messages after 24 hours'

    def handle(self, *args, **options):
        dt = timezone.now()
        expired_messages = EmailStorage.objects.filter(expiration__lt=dt)

        logger.debug(f"{len(expired_messages)} user messages to clear")
        for user_messages in expired_messages:
            user_messages.raw_emails = None
            user_messages.parsed_emails = None
            user_messages.expiration = None
            user_messages.parse_status = 'ns'
            user_messages.save()
