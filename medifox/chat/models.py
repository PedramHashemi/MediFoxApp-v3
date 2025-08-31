from django.db import models
from django.contrib.auth.models import User

INSURANCE_TYPE_CHOICES = [
        ('private', 'Private'),
        ('public', 'Public'),
        ('none', 'Not Insured'),
    ]

class Insurance(models.Model):
    name = models.CharField(default='self_payer', max_length=50)


class Patient(models.Model):
    username = models.CharField(blank=False, null=False, max_length=50)
    password = models.CharField(blank=False, null=False, max_length=100)
    first_name = models.CharField(blank=False, null=False, max_length=30)
    last_name = models.CharField(blank=False, null=False, max_length=30)
    email = models.EmailField(blank=False, null=False, max_length=50)
    insurance = models.ForeignKey(Insurance, on_delete=models.PROTECT)
    insurance_type = models.CharField(max_length=20, choices=INSURANCE_TYPE_CHOICES, default='public')
    birth_date = models.DateField(null=True)


class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    message = models.TextField()
    user_is_sender = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    parent_message_id = models.ForeignKey('self', on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f"From {self.user} to {self.timestamp} sent by {self.user if self.user_is_sender else 'dora'}"
