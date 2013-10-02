from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

class message(models.Model):

    recipient = models.ForeignKey(User)
    message = models.CharField(null=False, blank=False, max_length=350)
    subject = models.CharField(null=True, blank=True,  max_length=90)
    hidden = models.BooleanField(null=False, default=False)