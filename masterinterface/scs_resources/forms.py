import os
from django.db import models
from django.contrib import admin
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from masterinterface.scs_resources.models import Resource, Workflow
from masterinterface.atos.metadata_connector import set_resource_metadata, update_resource_metadata


class ResourceForm(forms.ModelForm):

    name = forms.CharField(label="Resource Name", required=True)
    description = forms.CharField(label="Resource Description", required=True, widget=forms.Textarea)
    category = forms.CharField(help_text="Workflow Category", required=True, label="Category *")
    tags = forms.CharField(help_text="Add tags,separated by comma", required=False, label="Tags")
    semantic_annotations = forms.CharField(help_text="Add the annotations uri, separated by comma ", required=False, label="Semantic annotations")
    licence = forms.CharField(help_text="licence type for this workflow, es. GPL, BSD, MIT .. ", required=True, label='Licence *')

    class Meta:
        model = Resource
        exclude = ('global_id', 'owner', 'security_policy', 'security_configuration')

    def save(self, commit=True, owner=None):
        resource = super(ResourceForm, self).save(commit=False)
        metadata_payload = {
            'name': self.data['name'],
            'description': self.data['description'],
            'author': owner.username,
            'category': self.data['category'],
            'tags': self.data['tags'],
            'semantic_annotations': self.data['semantic_annotations'],
            'licence': self.data['licence'],
            'local_id': '',
            'type': ''
        }
        resource.global_id = set_resource_metadata(metadata_payload)
        resource.owner = owner
        if commit:
            resource.save()
        return resource


class WorkflowForm(ResourceForm):

    def is_valid(self):
        super_is_valid = super(ResourceForm, self).is_valid()
        if not os.path.splitext(self.cleaned_data['t2flow'].name)[1].lower().count("t2flow"):
            # TODO personalize field error message
            return False
        if not os.path.splitext(self.cleaned_data['xml'].name)[1].lower().count("xml"):
            # TODO personalize field error message
            return False

        return super_is_valid

    class Meta(ResourceForm.Meta):
        model = Workflow

    def __init__(self, *args, **kwargs):
        super(WorkflowForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            try:
                if name is 'xml':
                    field.widget.attrs["accept"] = ".xml"
                elif name is 't2flow':
                    field.widget.attrs["accept"] = ".t2flow"
            except:
                pass
