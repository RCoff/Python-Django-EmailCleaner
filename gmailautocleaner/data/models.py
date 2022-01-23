from django.db import models
from django_celery_results.models import TaskResult
import uuid


# Create your models here.
class EmailStorage(models.Model):
    CHOICES = [
        ('ns', 'Not Started'),
        ('ip', 'In Progress'),
        ('cp', 'Complete'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_email = models.EmailField(unique=True, editable=False)
    raw_emails = models.JSONField(null=True, blank=True)
    raw_emails_retrieval_time = models.DateTimeField(null=True, blank=True)
    parsed_emails = models.JSONField(null=True, blank=True)
    parse_status = models.CharField(max_length=2, choices=CHOICES, default='ns')
    expiration = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    task = models.ForeignKey(TaskResult, blank=True, null=True, on_delete=models.SET_NULL)

    def ready(self):
        return self.parse_status == 'cp'

    def clear(self):
        self.raw_emails = None
        self.raw_email_retrieval_time = None
        self.parsed_emails = None
        self.parse_status = 'ns'
        self.expiration = None
        self.task = None
        self.save()

    def __str__(self):
        return f"{self.user_email} - {self.id}"
