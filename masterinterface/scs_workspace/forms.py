__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'

from django import forms
from models import TavernaExecution


class TavernaExecutionForm(forms.ModelForm):

    class Meta:
        model = TavernaExecution
        exclude = ['owner', 't2flow', 'baclava', 'status', 'taverna_id', 'as_config_id', 'url']
        widgets = {
            'workflowId': forms.HiddenInput()
        }

    default_inputs = forms.BooleanField(label="Default Inputs", help_text="Check if you want to run this workflow with your inputs")
    inputFile = forms.FileField(label="Input definition", help_text="Input definition file, *.xml")



