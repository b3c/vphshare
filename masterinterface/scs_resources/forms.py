import os
from django.db import models
from django.contrib import admin
from django import forms
from django.conf import settings
from django.contrib.auth.models import User, Group
from masterinterface.scs_resources.models import Resource, Workflow
from masterinterface.atos.metadata_connector import set_resource_metadata, update_resource_metadata
from django_select2 import Select2MultipleChoiceField, Select2MultipleWidget

class ResourceForm(forms.ModelForm):

    name = forms.CharField(label="Resource Name", required=True)
    description = forms.CharField(label="Resource Description", required=True, widget=forms.Textarea)
    category = forms.CharField(help_text="Resource Category", required=False, label="Category")
    tags = forms.CharField(help_text="Tags (separated by comma)", required=False, label="Tags")
    semantic_annotations = forms.CharField(help_text="The annotations uri (separated by comma)", required=False, label="Semantic annotations")
    licence = forms.CharField(help_text="Licence type (es. GPL, BSD, MIT, ..)", required=True, label='Licence *')

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
            'type': resource.__class__.__name__
        }

        try:
            update_resource_metadata(self.instance.global_id, metadata_payload)
        except Exception, e:
            resource.global_id = set_resource_metadata(metadata_payload)
            resource.owner = owner

        if commit:
            resource.save()
        return resource


class WorkflowForm(ResourceForm):

    def is_valid(self):
        super_is_valid = super(ResourceForm, self).is_valid()
        if getattr(self, 'instance', None) and getattr(self, 'cleaned_data', None):
            if not os.path.splitext(self.cleaned_data['t2flow'].name)[1].lower().count("t2flow"):
                # TODO personalize field error message
                return False
            if not os.path.splitext(self.cleaned_data['xml'].name)[1].lower().count("xml"):
                # TODO personalize field error message
                return False
        if getattr(self, 'cleaned_data', None):
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


class UsersGroupsForm(forms.Form):

    Usersinput = Select2MultipleChoiceField()

    def __init__(self, id="", list=[], excludedList=[], *args, **kwargs):

        users = User.objects.all()
        groups = Group.objects.all()

        usersList = [("user_"+str(user.username),  "%s %s" % (user.first_name, user.last_name)) for user in users if user not in excludedList]
        groupList = [("group_"+str(group.name),  "%s" % group.name) for group in groups if group not in excludedList]
        usersList.sort(key=lambda tup: tup[1])
        groupList.sort(key=lambda tup: tup[1])

        self.base_fields['Usersinput'] = Select2MultipleChoiceField(choices=[('Users',usersList), ('Groups',groupList)], label="")
        self.base_fields['Usersinput'].widget.attrs = {'id':id}
        super(UsersGroupsForm, self).__init__(*args, **kwargs)
