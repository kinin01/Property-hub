from django.db import models
from a_users.models import CustomUser

# Create your models here.
class Notification(models.Model):
    is_read = models.BooleanField(default=False)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    recipients = models.ManyToManyField(CustomUser, related_name='notifications')
