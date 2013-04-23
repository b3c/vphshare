from django.db import models

# Create your models here.

from django import forms
from django.conf import settings
from django.contrib.auth.models import User


class scsWorkflow(models.Model):

    title = models.CharField(verbose_name="Title", max_length=125, null=False, blank=False)
    description = models.TextField(verbose_name="Description", blank=True, null=True)
    t2flow = models.FileField(verbose_name="Taverna workflow", upload_to=settings.MEDIA_ROOT)
    xml = models.FileField(verbose_name="Input definition", upload_to=settings.MEDIA_ROOT)
    metadataId = models.PositiveIntegerField(null=True)
    user = models.ForeignKey(User)


class scsWorkflowForm(forms.ModelForm):

    #objtype = forms.CharField()
    #name = forms.CharField()
    #description = forms.Textarea()
    author = forms.CharField()
    category = forms.CharField()
    tags = forms.CharField()
    semantic_annotations = forms.CharField()
    licence = forms.CharField()
    #rating = forms.CharField()
    #views = forms.CharField()
    #local_id = forms.CharField()

    class Meta:
        model = scsWorkflow
        exclude = ('metadataId','user')