__author__ = 'Teo'

from django import forms
from models import Study, Institution, VPHShareSmartGroup
from permissions.utils import add_local_role
from config import *
from django.contrib.admin import ModelAdmin
from datetimewidget.widgets import DateTimeWidget
from django_select2 import Select2MultipleChoiceField
from django.contrib.auth.models import User

my_default_errors = {
    'required': 'This field is required',
    'invalid': 'Enter a valid value'
}


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
        updateUser_set(obj, obj.managers.all())


class StudyForm(forms.ModelForm):
    name = forms.CharField(required=True, label="Title", help_text="Study title")

    def __init__(self, usersset = [], *args, **kwargs):

        usersList = [(user.id,  "%s %s" % (user.last_name, user.first_name)) for user in usersset ]
        usersList.sort(key=lambda tup: tup[1])
        self.base_fields['managers'] = Select2MultipleChoiceField(choices=usersList)
        super(StudyForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        super(StudyForm, self).save(commit=commit)
        super(StudyForm, self).save()
        self.save_m2m()
        updateUser_set(self.instance, self.instance.managers.all())
        return self.instance

    class Meta:
        dateTimeOptions = {
            'format': 'dd/mm/yyyy',
            'autoclose': 'true',
            'minView': '2',
        }
        model = Study
        widgets = {
            'permissions': forms.HiddenInput(),
            'institution': forms.HiddenInput(),
            'start_date': DateTimeWidget(options=dateTimeOptions, attrs={'id': 'study_start'}),
            'finish_date': DateTimeWidget(options=dateTimeOptions, attrs={'id': 'study_end'}),
        }
        exclude = ['parent', 'active']



class StudyAdmin(ModelAdmin):
    def save_model(self, request, obj, form, change):
        super(StudyAdmin, self).save_model(request, obj, form, change)
        form.save_m2m()
        updateUser_set(obj, obj.managers.all())


class InstitutionForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):

        users = User.objects.all()
        usersList = [(user.id,  "%s %s" % (user.last_name, user.first_name)) for user in users]
        usersList.sort(key=lambda tup: tup[1])
        self.base_fields['managers'] = Select2MultipleChoiceField(choices=usersList)
        super(InstitutionForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = self.cleaned_data
        # Check 1: Must have valid user.
        # To Be Developed
        return cleaned_data

    def save(self, commit=True):
        super(InstitutionForm, self).save(commit)
        super(InstitutionForm, self).save()
        self.save_m2m()
        updateUser_set(self.instance, self.instance.managers.all())
        return self.instance

    class Meta:
        model = Institution

        widgets = {
            'permissions': forms.HiddenInput(),
            # 'managers': forms.HiddenInput(),
        }
        exclude = ['parent', 'active']


class UserFinder(forms.Form):

    Usersinput = Select2MultipleChoiceField()
    areManagers = forms.BooleanField(label="Set as managers? ", required=False)

    def __init__(self, list=[], exclude=[], *args, **kwargs):
        if not list:
            excludedList = []
            if exclude:
                for u in exclude[0]:
                    excludedList.append(u.user_id)
                for u in exclude[1]:
                    excludedList.append(u.id)

            users = User.objects.all()
            usersList = [(user.id,  "%s %s" % (user.first_name, user.last_name)) for user in users if user.id not in excludedList]
            id="groupuserlist"
        else:
            usersList = [(user.id,  "%s %s" % (user.first_name, user.last_name)) for user in list ]
            id="studyuserlist"

        usersList.sort(key=lambda tup: tup[1])
        self.base_fields['Usersinput'] = Select2MultipleChoiceField(choices=usersList, label= 'Add users to institution')

        super(UserFinder, self).__init__(*args, **kwargs)


class StudyUserFinder(forms.Form):

    StudyUsersinput = Select2MultipleChoiceField()
    areManagers = forms.BooleanField(label="Set as managers? ", required=False)

    def __init__(self, list=[], exclude=[], *args, **kwargs):

        excludedList = []
        if exclude:
            for u in exclude[0]:
                excludedList.append(u.user_id)
            for u in exclude[1]:
                excludedList.append(u.id)

        users = User.objects.all()
        usersList = [(user.id,  "%s %s" % (user.first_name, user.last_name)) for user in list if user.id not in excludedList]

        usersList.sort(key=lambda tup: tup[1])
        self.base_fields['StudyUsersinput'] = Select2MultipleChoiceField(choices=usersList, label= 'Add users to study')

        super(StudyUserFinder, self).__init__(*args, **kwargs)


class InstitutionAdmin(ModelAdmin):
    def save_model(self, request, obj, form, change):
        super(InstitutionAdmin, self).save_model(request, obj, form, change)
        form.save_m2m()
        updateUser_set(obj, obj.managers.all())