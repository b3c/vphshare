from django import forms

class LobcderUpload(forms.Form):
    file = forms.FileField(required = True)

class LobcderDelete(forms.Form):
    pass

class LobcderCreateDirectory(forms.Form):
    name = forms.CharField(required = True)