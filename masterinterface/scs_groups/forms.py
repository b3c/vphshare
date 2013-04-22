__author__ = 'Teo'

from django import forms
from models import Study, Institution, VPHShareSmartGroup
from permissions.utils import add_local_role
from config import *
from django.contrib.admin import ModelAdmin


def updateUser_set(obj, managers):
    for manager in managers:
        obj.user_set.add(manager)
        add_local_role(obj, manager, group_manager)


class VPHShareSmartGroupForm(forms.ModelForm):

    def save(self, commit=True):
        super(VPHShareSmartGroupForm, self).save()
        updateUser_set(self.instance, self.instance.managers.all())
        return self.instance

    class Meta:
        model = VPHShareSmartGroup


class VPHShareSmartGroupAdmin(ModelAdmin):

    def save_model(self, request, obj, form, change):
        super(VPHShareSmartGroupAdmin, self).save_model(request, obj, form, change)
        form.save_m2m()
        updateUser_set(obj,  obj.managers.all())


class StudyForm(forms.ModelForm):

    def save(self, commit=True):
        super(StudyForm, self).save()
        updateUser_set(self.instance, self.instance.principals.all())
        return self.instance

    class Meta:
        model = Study
        widgets = {
            'permissions': forms.HiddenInput(),
            'institution': forms.HiddenInput(),
        }


class StudyAdmin(ModelAdmin):

    def save_model(self, request, obj, form, change):
        super(StudyAdmin, self).save_model(request, obj, form, change)
        form.save_m2m()
        updateUser_set(obj,  obj.managers.all())


class InstitutionForm(forms.ModelForm):

    def save(self, commit=True):
        super(InstitutionForm, self).save()
        updateUser_set(self.instance, self.instance.managers.all())
        return self.instance

    class Meta:
        model = Institution

        widgets = {
            'permissions': forms.HiddenInput(),
            # 'managers': forms.HiddenInput(),
            }


class InstitutionAdmin(ModelAdmin):

    def save_model(self, request, obj, form, change):
        super(InstitutionAdmin, self).save_model(request, obj, form, change)
        form.save_m2m()
        updateUser_set(obj,  obj.managers.all())