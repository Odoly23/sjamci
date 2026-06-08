# notification/models.py

from django.db import models
from django.contrib.auth.models import User
from custom.models import BaseModel

class Notification(BaseModel):
    TYPE_CHOICES = (
        ('PEDIDU', 'Pedidu'),
        ('FUND', 'Fund Usage'),
        ('CASHFLOW', 'Cash Flow'),
        ('BOOK', 'Financial Book'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    receiver = models.ForeignKey(User,  on_delete=models.CASCADE, related_name='received_notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notif_type = models.CharField(max_length=20,  choices=TYPE_CHOICES )
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255,   blank=True, null=True)

    def __str__(self):
        return self.title