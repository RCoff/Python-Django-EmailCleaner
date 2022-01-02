from django.db import models
import uuid


# Create your models here.
class EmailStorage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_email = models.EmailField()
    raw_emails = models.JSONField()
    parsed_emails = models.JSONField()
    expiration = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
