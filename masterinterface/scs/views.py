from django.http import HttpResponseRedirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.messages.api import get_messages

from scs import __version__ as version
from masterinterface import settings


def home(request):
    """Home view, displays login """
    if request.user.is_authenticated():
        return HttpResponseRedirect('done')
    else:
        return render_to_response('scs/index.html', {'version': version},
            RequestContext(request))

@login_required
def done(request):
    """Login complete view, displays user data"""
    ctx = {
        'version': version,
        'last_login': request.session.get('social_auth_last_login_backend')
    }
    return render_to_response('scs/done.html', ctx, RequestContext(request))

def error(request):
    """Error view"""
    messages = get_messages(request)
    return render_to_response('scs/error.html', {'version': version, 'messages': messages},
        RequestContext(request))

def logout(request):
    """Logs out user"""
    auth_logout(request)
    return HttpResponseRedirect('/')


def bt_login(request):
    if request.method == 'POST' and request.POST.get('username'):
        name = settings('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY', 'partial_pipeline')
        request.session['saved_username'] = request.POST['username']
        backend = request.session[name]['backend']
        return redirect('socialauth_complete', backend=backend)

    return render_to_response('scs/bt_login.html',
            {'version': version},
        RequestContext(request)
    )

def test(request):
    return render_to_response("scs/test.html", {'ajax':request.is_ajax}, RequestContext(request))

def services(request):
    serviceList = []

    for app in settings.INSTALLED_APPS:
        # TODO do a better check
        if app.count('masterinterface') and not app.count('scs'):
            service = app.split('.')[1]
            serviceList.append( service )

    return render_to_response("scs/services.html",
            {'services':serviceList},
        RequestContext(request))
