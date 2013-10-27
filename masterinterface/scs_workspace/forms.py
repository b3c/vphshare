__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'

from django import forms
from models import TavernaExecution


class TavernaExecutionForm(forms.ModelForm):

    class Meta:
        model = TavernaExecution
        exclude = ['owner', 't2flow', 'baclava', 'workflowId', 'status']

    default_inputs = forms.BooleanField(label="Default Inputs", help_text="Check if you want to run this workflow with the default inputs")
    workflow_id = forms.IntegerField(widget=forms.HiddenInput)



