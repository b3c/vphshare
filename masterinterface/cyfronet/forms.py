from django import forms

class LobcderUpload(forms.Form):
    file = forms.FileField(required = True)