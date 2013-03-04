__author__ = 'Teo'

from django import forms
from models import Study, Institution


class StudyForm(forms.ModelForm):

    class Meta:
        model = Study
        widgets = {
            'permissions': forms.HiddenInput(),
            'institution': forms.HiddenInput(),
        }


class InstitutionForm(forms.ModelForm):

    class Meta:
        model = Institution

        widgets = {
            'permissions': forms.HiddenInput(),
            # 'managers': forms.HiddenInput(),
            }