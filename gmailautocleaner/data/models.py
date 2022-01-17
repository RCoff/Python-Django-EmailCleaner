from django.db import models
import uuid


# Create your models here.
class EmailStorage(models.Model):
    CHOICES = [
        ('ns', 'Not Started'),
        ('ip', 'In Progress'),
        ('cp', 'Complete'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_email = models.EmailField(unique=True, editable=False)
    raw_emails = models.JSONField(null=True, blank=True)
    raw_emails_retrieval_time = models.DateTimeField(null=True, blank=True)
    parsed_emails = models.JSONField(null=True, blank=True)
    parse_status = models.CharField(max_length=2, choices=CHOICES, default='ns')
    expiration = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    task_id = models.UUIDField(blank=True, null=True)

    def ready(self):
        return self.parse_status == 'cp'

    def clear(self):
        self.raw_emails = None
        self.raw_email_retrieval_time = None
        self.parsed_emails = None
        self.parse_status = 'ns'
        self.expiration = None
        self.task_id = None
        self.save()

    def __str__(self):
        return f"{self.user_email} - {self.id}"


class ParsedEmail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    raw_emails = models.ForeignKey(EmailStorage, on_delete=models.CASCADE)
    message = models.JSONField()

    def __str__(self):
        return f"{self.raw_emails.user_email} - {self.raw_emails_id}"

