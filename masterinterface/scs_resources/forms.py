import os
from django.db import models
from django.contrib import admin
from django import forms
from django.conf import settings
from django.contrib.auth.models import User, Group
from masterinterface.scs_groups.models import Institution, Study
from masterinterface.scs_resources.models import Resource, Workflow
from masterinterface.atos.metadata_connector_json import set_resource_metadata, update_resource_metadata
from django_select2 import Select2MultipleChoiceField, Select2ChoiceField, HeavySelect2TagField, HeavySelect2MultipleChoiceField
from django_select2.widgets import Select2Mixin
from django.core.files.storage import default_storage
from masterinterface.scs_resources.widgets import AdditionalFile, AdditionalLink
from django.core.cache import cache


class Select2CommaTags(Select2Mixin, forms.TextInput):

    def __init__(self, **kwargs):
        select2_options = kwargs.pop('select2_options', {})
        select2_options['tokenSeparators']=[","]
        select2_options['tags']=[""]
        kwargs['select2_options'] = select2_options
        super(Select2CommaTags, self).__init__(**kwargs)

    def init_options(self):
            self.options.pop('multiple', None)

class ResourceForm(forms.ModelForm):

    name = forms.CharField(label="Name *", required=True)
    description = forms.CharField(label="Description *", required=True, widget=forms.Textarea)
    licence = Select2ChoiceField(choices=(('BSD','Berkeley Software Distribution'), ('MIT','MIT license'), ('GPL','General Public License'), ('LGPL','Lesser General Public License'), ('EDU','Academic, educational license'), ('GOV', 'Government license'),('EULA','End-user License Agreement'),('OLP','Microsoft Open License Program'),('TLP','Transactional Licensing Program'),('VLP','Volume License Program')), help_text="Licence type", required=True, label='Licence *', initial="")
    category = Select2ChoiceField(choices=(('Cardiovascular', 'Cardiovascular'), ('Respiratory','Respiratory'),('Genetics','Genetics'),('Infection and Immunology', 'Infection & Immunology'), ('Musculoskeletal', 'Musculoskeletal'), ('Gastroenerology','Gastroenerology'),('Neurology','Neurology') ,('Oncology','Oncology'), ('Multidisciplinary','Multidisciplinary') ,('Information Technology','Information Technology')), help_text="Category", required=False, label="Category", initial="")
    tags = forms.CharField(widget=Select2CommaTags(), required=False, label="Tags", help_text="Type tags")
    semanticAnnotations = forms.CharField(widget=Select2CommaTags(), required=False, label="Semantic annotations", help_text="Type concept URI")
    resourceURL = forms.URLField(required=False, help_text="Resource URL", label="Resource URL")
    type = forms.CharField(widget=forms.HiddenInput)
    author = forms.CharField(widget=forms.HiddenInput)
    localID = forms.CharField(widget=forms.HiddenInput, required=False)
    relatedResources = HeavySelect2MultipleChoiceField(help_text="Search for related resources", required=False, label="Related resources", data_view="smart_get_resources", choices=())

    class Meta:
        model = Resource
        exclude = ('global_id', 'owner', 'security_policy', 'security_configuration')
        relatedChoice = ()

    def __init__(self, *args, **kwargs):
        super(ResourceForm, self).__init__(*args, **kwargs)
        if self.data.get('type', None) is not None and self.data.get('type', None) == 'AtomicService':
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['description'].widget.attrs['readonly'] = True
        if self.data.get('relatedResources',None) is not None:
            try:
                relatedResources = self.data.getlist('relatedResources')
                for global_id in relatedResources:
                    try:
                        r = Resource.objects.get(global_id=global_id)
                    except Exception, e:                        
                        continue
                    self.fields['relatedResources'].choices += ((global_id,r.metadata['name']),)
            except Exception, e:
                relatedResources = self.data['relatedResources']
                self.data['relatedResources'] = []
                for global_id in relatedResources:
                    try:
                        r = Resource.objects.get(global_id=global_id['resourceID'])
                    except Exception, e:
                        continue                                            
                    self.fields['relatedResources'].choices += ((global_id['resourceID'],r.metadata['name']),)
                    self.data['relatedResources'].append(global_id['resourceID'])
        if self.data.get('semanticAnnotations',None) is not None:
            try:
                relatedResources = self.data['semanticAnnotations']
                self.data['semanticAnnotations'] = ''
                for conceptURI in relatedResources:
                    if self.data['semanticAnnotations'] == '':
                        self.data['semanticAnnotations'] = conceptURI['conceptURI']
                    else:
                        self.data['semanticAnnotations'] = ','.join([self.data['semanticAnnotations'],conceptURI['conceptURI']])
            except Exception, e:
                pass
        #decompose Additional component - Link
        new_link = AdditionalLink().value_from_datadict(self.data, self.files, 0)
        #decompose Additional component - File
        new_file = AdditionalFile().value_from_datadict(self.data, self.files, 0)
        if self.data.get('linkedTo', None) is None or new_link or new_file:
            #if linkedTo is empty or user post new values
            self.data['linkedTo'] = []
            self.data['linkedTo'] += [{'link':{'linkURI':linkURI,'linkType':linkType}} for linkType, linkURI in new_link]
            for fileDescription, filePayLoad in new_file:
                path = default_storage.save(''.join(['./additionalFiles/',filePayLoad.name]),filePayLoad)
                fileURI = ''.join([settings.BASE_URL, default_storage.url(path)])
                self.data['linkedTo'] += [{'link':{'linkURI':fileURI,'linkType':fileDescription}} ]
        else:
            #if the form is load for first time
            linkedTo = self.data['linkedTo']
            self.data['linkedTo'] = []
            for link in linkedTo:
                self.data['linkedTo'] += [{'link':{'linkURI':link['linkURI'],'linkType':link['linkType']}}]




    def save(self, commit=True, owner=None, additional_metadata = None):
        if not additional_metadata: additional_metadata = {}
        resource = super(ResourceForm, self).save(commit=False)
        metadata_payload = {
            'name': self.data['name'],
            'description': self.data['description'],
            'author': owner.username,
            'category': self.data['category'],
            'tags': self.data['tags'],
            'semanticAnnotations': [ {'semanticConcept':{'conceptURI':conceptURI}} for conceptURI in self.data['semanticAnnotations'].split(',') if str(conceptURI) is not ''],
            'licence': self.data['licence'],
            'localID': self.data['localID'],
            'resourceURL': self.data['resourceURL'],
            'type': self.data['type'],
            'relatedResources': [{'relatedResource':{'resourceID':gId}} for gId in self.data.getlist('relatedResources')],
            'linkedTo' :  self.data['linkedTo']
        }
        metadata_payload.update(additional_metadata)
        try:
            cache.delete(self.instance.global_id)
            if self.instance.global_id is None:
                raise Exception()
            update_resource_metadata(self.instance.global_id, metadata_payload, metadata_payload['type'])
        except Exception, e:
            if self.instance.global_id is not None:
                raise e
            resource.global_id = set_resource_metadata(metadata_payload, metadata_payload['type'])
            resource.owner = owner

        if commit:
            resource.save()
        return resource

class DatasetForm(ResourceForm):
    sparqlEndPoint = forms.URLField(required=True, label="SPARQL endpoint *", help_text="endpoint URI")

    def save(self, commit=True, owner=None, additional_metadata = None):
        if not additional_metadata: additional_metadata = {}
        additional_metadata['sparqlEndPoint'] = self.data['sparqlEndPoint']
        super(DatasetForm, self).save(commit, owner, additional_metadata)

class SWSForm(ResourceForm):
    semanticWebServiceType = Select2ChoiceField(choices=(('Rest','Rest'),('Soap','Soap')), help_text="", required=True, label='SWS type', initial="Rest")
    semanticWebServiceURL = forms.URLField(required=True, label="SWS url *", help_text="semantic web service URL")

    def save(self, commit=True, owner=None, additional_metadata=None):
        if not additional_metadata: additional_metadata = {}
        additional_metadata['semanticWebServiceType'] = self.data['semanticWebServiceType']
        additional_metadata['semanticWebServiceURL'] = self.data['semanticWebServiceURL']
        super(SWSForm, self).save(commit, owner, additional_metadata)

class WorkflowForm(ResourceForm):

    def is_valid(self):
        super_is_valid = super(WorkflowForm, self).is_valid()
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

        users = User.objects.all().exclude(username='admin')
        groups = Institution.objects.all()
        usersList = [("user_"+str(user.username),  "%s %s (%s)" % (user.first_name, user.last_name, user.username)) for user in users if user not in excludedList]
        groupList = [("group_"+str(group.name),  "%s" % group.name) for group in groups if group not in excludedList]
        groups = Study.objects.all()
        groupList += [("group_"+str(group.name),  "%s" % group.name) for group in groups if group not in excludedList]
        usersList.sort(key=lambda tup: tup[1])
        groupList.sort(key=lambda tup: tup[1])

        self.base_fields['Usersinput'] = Select2MultipleChoiceField(choices=[('Users',usersList), ('Groups',groupList)], label="")
        self.base_fields['Usersinput'].widget.attrs = {'id':id}
        super(UsersGroupsForm, self).__init__(*args, **kwargs)

