from django.contrib import admin
from .models import Insurance, Patient, ChatMessage


# admin.site.unregister(User)
admin.site.register(Insurance)
admin.site.register(Patient)
admin.site.register(ChatMessage)
