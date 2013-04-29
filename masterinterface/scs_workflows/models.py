from django.db import models
from django.contrib import admin
# Create your models here.

from django import forms
from django.conf import settings
from django.contrib.auth.models import User


class scsWorkflow(models.Model):

    title = models.CharField(verbose_name="Title *", max_length=125, null=False, blank=False)
    description = models.TextField(verbose_name="Description *", blank=True, null=True, help_text="Workflow description")
    t2flow = models.FileField(verbose_name="Taverna workflow *", upload_to='./taverna_workflows/',
                              help_text="Taverna workflow file, *.t2flow")
    xml = models.FileField(verbose_name="Input definition *", upload_to='./workflows_input/',
                           help_text="Input definition file, *.xml")
    metadataId = models.CharField(null=True, max_length=39)
    user = models.ForeignKey(User, default=1)


class scsWorkflowForm(forms.ModelForm):

    #objtype = forms.CharField()
    #name = forms.CharField()
    #description = forms.Textarea()
    #author = forms.CharField()
    category = forms.CharField(help_text="Workflow Category")
    tags = forms.CharField(help_text="Add tags,separated by comma")
    semantic_annotations = forms.CharField(help_text="Add the annotations uri, separated by comma ")
    licence = forms.CharField(help_text="licence type for this workflow, es. GPL, BSD, MIT .. ")
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