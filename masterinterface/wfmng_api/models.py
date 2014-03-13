from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

class WfMngApiModel(models.Model):
    global_id = models.CharField(max_length=255)

    def __unicode__(self):
        return self.global_id

admin.site.register(WfMngApiModel)
