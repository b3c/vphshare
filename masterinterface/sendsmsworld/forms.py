from django import forms
from models import sendSMS

class sendSMSForm( forms.ModelForm):
    """ sendSMS request form """

    class Meta:
        model = sendSMS

