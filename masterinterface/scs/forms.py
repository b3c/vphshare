from django import forms


class ContactUs(forms.Form):
    subject = forms.CharField(max_length=100, required=True, label="Subject")
    description = forms.CharField(max_length=400,help_text="Describe what happened", required=False, label="Description", initial="", widget=forms.Textarea)
    page = forms.CharField(help_text="page URL of the problem", required=False, label="URL", initial="")
    browser = forms.CharField(max_length=300, required=False, widget=forms.HiddenInput, label="browser")
    userID = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput, label="user")
    sentryid = forms.CharField(max_length=200, required=False, widget=forms.HiddenInput, label="sentry trace id")

    def __init__(self, request, *args, **kwargs):
        super(ContactUs, self).__init__(*args, **kwargs)
        self.data['browser'] = request.META['HTTP_USER_AGENT']
        if request.user.is_authenticated():
            self.data['userID'] = request.user.username
        if getattr(request,'sentry',None) is not None:
            # self.data['sentryid'] = request.sentry.id
            pass
