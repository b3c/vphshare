from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class ParaviewInstance(models.Model):
    pid = models.IntegerField(blank=False, null=False)
    port = models.IntegerField(blank=False, null=False)
    user = models.ForeignKey(User)
    creation_time = models.DateTimeField(auto_now=True)
    deletion_time = models.DateTimeField(null=True, default=None, blank=True )