__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'

from django import forms


class PropertyForm(forms.Form):

    listening_port = forms.IntegerField(required=False, help_text="Listening Port")
    outgoing_address = forms.CharField(required=False, help_text="Outgoing Address")
    outgoing_port = forms.CharField(required=False, help_text="Outgoing Port")
    configuration_file = forms.CharField(max_length=2048, widget=forms.Textarea, help_text='Configuration File')

