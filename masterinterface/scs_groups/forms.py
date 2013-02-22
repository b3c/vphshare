__author__ = 'Teo'

from django import forms
from models import Study


class StudyForm(forms.ModelForm):

    class Meta:
        model = Study
        widgets = {
            'permissions': forms.HiddenInput(),
            'institution': forms.HiddenInput(),
        }
