from django.db import models
from django.contrib import admin
# Create your models here.

from django import forms
from django.conf import settings
from django.contrib.auth.models import User


class scsWorkflow(models.Model):

    title = models.CharField(verbose_name="Title", max_length=125, null=False, blank=False)
    description = models.TextField(verbose_name="Description", blank=True, null=True)
    t2flow = models.FileField(verbose_name="Taverna workflow", upload_to='./taverna_workflows/')
    xml = models.FileField(verbose_name="Input definition", upload_to='./workflows_input/')
    metadataId = models.CharField(null=True, max_length=39)
    user = models.ForeignKey(User, default=1)


class scsWorkflowForm(forms.ModelForm):

    #objtype = forms.CharField()
    #name = forms.CharField()
    #description = forms.Textarea()
    #author = forms.CharField()
    category = forms.CharField()
    tags = forms.CharField()
    semantic_annotations = forms.CharField()
    licence = forms.CharField()
    #rating = forms.CharField()
    #views = forms.CharField()
    #local_id = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(scsWorkflowForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            try:
                if name is 'xml':
                    field.widget.attrs["accept"] = ".xml"
                elif name is 't2flow':
                    field.widget.attrs["accept"] = ".t2flow"
            except:
                pass

    class Meta:
        model = scsWorkflow

        exclude = ('metadataId','user')


admin.site.register(scsWorkflow)