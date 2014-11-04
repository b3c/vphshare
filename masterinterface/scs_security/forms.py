__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'

from django import forms
from django.forms import widgets
from permissions.models import Role
from datetimewidget.widgets import DateWidget, TimeWidget
from masterinterface.scs_security.widgets import AdditionalUserAttribute, AdditionalPostField


class AdvancePolicyForm(forms.Form):
    advance_user = forms.BooleanField(label='Expert mode', required=False, initial=True, help_text='Disabling the expert mode you will lose the uploaded file')
    name = forms.CharField(label='Policy name', required=True)
    advanced_xacml_upload = forms.FileField(label="Upload the xacml file", required=True)

class PolicyForm(forms.Form):

    advance_user = forms.BooleanField(label='Expert mode', required=False, help_text='Enabling the expert mode you can upload your own xacml file but  you will lose the information in this form.')
    name = forms.CharField(label='Policy name', required=True)
    role = forms.ModelChoiceField(queryset=Role.objects.all() , label="Roles equals to", required=True)
    user_attributes = forms.CharField(label="User attributes", required=False)
    expiry = forms.DateField(label= "Expiry date", widget=DateWidget(usel10n=False, options={'format':'yyyy-mm-dd'}), required=False)
    time_start = forms.TimeField(label = "Working time starts", widget= TimeWidget(usel10n=False, options={'format':'hh:mm'}), required=False)
    time_end = forms.TimeField(label = "Working time ends", widget= TimeWidget(usel10n=False, options={'format':'hh:mm'}), required=False)
    url_contain = forms.CharField(label="URL contains", required=False)
    post_fields = forms.CharField(label="Post Fields", required=False)

    def __init__(self, policy=None,  *args, **kwargs):
        #if policy is not None:
        super(PolicyForm,self).__init__(*args,**kwargs)

    def clean(self):
        if self.cleaned_data.get('time_start', None) is not None and self.cleaned_data.get('time_end', None) is None :
            self._errors['time_end'] = self.error_class(['If you set time start you have also to set time end'])
        if self.cleaned_data.get('time_start', None) is None and self.cleaned_data.get('time_end', None) is not None :
            self._errors['time_start'] = self.error_class(['If you set time end you have also to set time start'])
        if self.cleaned_data.get('time_start', None) and self.cleaned_data.get('time_end', None):
            if self.cleaned_data.get('time_start', None) > self.cleaned_data.get('time_end', None):
                self._errors['time_end'] = self.error_class(['Time end have to be after time start'])

        additional_user_attributes = AdditionalUserAttribute().value_from_datadict(self.data, self.files, 0)
        #Load user_attributes from the data
        if self.data.get('UserAttribute', None) is None or  additional_user_attributes:
            self.data['UserAttribute'] = []
            for additional_user_attribute in additional_user_attributes:
                self.data['UserAttribute'] += [AdditionalUserAttribute().render(0,additional_user_attribute)]
                if u'' in additional_user_attribute or None in additional_user_attribute:
                    self._errors['user_attributes'] = self.error_class(["User attribute can't be empty please fill in all fields or remove it"])

        additional_post_fields = AdditionalPostField().value_from_datadict(self.data, self.files, 0)
        #Load user_attributes from the data
        if self.data.get('PostFields', None) is None or  additional_post_fields:
            self.data['PostFields'] = []
            for additional_post_field in additional_post_fields:
                self.data['PostFields'] += [AdditionalPostField().render(0, additional_post_field)]
                if u'' in additional_post_field or None in additional_post_field:
                    self._errors['post_fields'] = self.error_class(["Post field can't be empty please fill in all fields or remove it"])
        return super(PolicyForm, self).clean()

    def is_valid(self):
        return super(PolicyForm, self).is_valid()


class PropertyForm(forms.Form):

    listening_port = forms.IntegerField(required=False, help_text="Listening Port")
    outgoing_address = forms.CharField(required=False, help_text="Outgoing Address")
    outgoing_port = forms.CharField(required=False, help_text="Outgoing Port")
    configuration_file = forms.CharField(max_length=2048, widget=forms.Textarea, help_text='Configuration File')

