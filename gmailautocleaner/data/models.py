from django.db import models
import uuid


# Create your models here.
class EmailStorage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_email = models.EmailField()
    messages_json = models.JSONField()
    created = models.DateTimeField(auto_now_add=True, editable=False)
