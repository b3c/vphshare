from django.http import HttpResponseRedirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.messages.api import get_messages

from scs import __version__ as version
from masterinterface import settings

from tktauth import createTicket, validateTicket
import binascii

def home(request):
    """Home view """

    data = {'version': version}

    if request.user.is_authenticated():
        data['last_login'] = request.session.get('social_auth_last_login_backend')

    return render_to_response(
        'scs/index.html',
        data,
        RequestContext(request)
    )

def login(request):
    """Login view"""

    return render_to_response(
        'scs/login.html',
        {'version': version, 'next': request.GET.get('next','/')},
        RequestContext(request)
    )

def done(request):
    """ login complete view """
    ctx = {
        'version': version,
        'last_login': request.session.get('social_auth_last_login_backend')
    }

    # create ticket
    tokens = ('foo','bar') #to be random generated
    user_data = '%s %s' % (request.user.first_name, request.user.last_name)
    tkt = createTicket(
        settings.SECRET_KEY,
        request.user.username,
        tokens=tokens,
        user_data=user_data
    )

    tkt64 = binascii.b2a_base64(tkt).rstrip()

    response = render_to_response(
        'scs/done.html',
        ctx,
        RequestContext(request)
    )

    response.set_cookie( 'vph-tkt', tkt64 )

    return response

@login_required
def profile(request):
    """Login complete view, displays user data"""

    tkt64 = request.COOKIES.get('vph-tkt','No ticket')

    data = {
        'version': version,
        'last_login': request.session.get('social_auth_last_login_backend'),
        'tkt64': tkt64
    }



    return render_to_response(
        'scs/profile.html',
        data,
        RequestContext(request)
    )

def login_error(request):
    """Very simpole login error view"""
    messages = get_messages(request)
    return render_to_response(
        'scs/error.html',
        {'version': version,
         'messages': messages},
        RequestContext(request)
    )

@login_required
def logout(request):
    """Logs out user"""
    auth_logout(request)
    return HttpResponseRedirect('/')


def bt_loginform(request):
    """ return the biomedtown login form """
    if request.method == 'POST' and request.POST.get('username'):
        name = settings('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY', 'partial_pipeline')
        request.session['saved_username'] = request.POST['username']
        backend = request.session[name]['backend']
        return redirect('socialauth_complete', backend=backend)

    return render_to_response('scs/bt_loginform.html',
            {'version': version},
        RequestContext(request)
    )
def bt_login(request):
    """ return the biomedtown login page with and embedded login iframe"""

    return render_to_response('scs/bt_login.html',
            {'version': version},
        RequestContext(request)
    )

def test(request):
    """ just a test page """
    return render_to_response("scs/test.html", {'ajax':request.is_ajax}, RequestContext(request))

def services(request):
    """ a page with all available applications """
    serviceList = []

    for app in settings.INSTALLED_APPS:
        # TODO do a better check
        if app.count('masterinterface') and not app.count('scs'):
            service = app.split('.')[1]
            serviceList.append( service )

    return render_to_response("scs/services.html",
            {'services':serviceList},
        RequestContext(request))

def contacts(request):
    return render_to_response("scs/contacts.html",
            {},
        RequestContext(request))

def help(request):
    return render_to_response("scs/help.html",
            {},
        RequestContext(request))

@login_required
def cloudmanager(request):
    return render_to_response("scs/cloudmanager.html",
            {'source': settings.CLOUD_PORTLET_LOGIN_URL_TEMPLATE.format(request.user.username, request.COOKIES.get('vph-tkt','No ticket'), 'cloud')},
        RequestContext(request))

@login_required
def datamanager(request):
    return render_to_response("scs/datamanager.html",
            {'source': settings.CLOUD_PORTLET_LOGIN_URL_TEMPLATE.format(request.user.username, request.COOKIES.get('vph-tkt','No ticket'), 'data')},
        RequestContext(request))