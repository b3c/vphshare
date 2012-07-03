from masterinterface import wsdl2mi
from django.http import HttpResponseRedirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.messages.api import get_messages
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from scs import __version__ as version
from masterinterface import settings

def home(request):
    """Home view """

    data = {'version': version}
    if request.user.is_authenticated():
        data['last_login'] = request.session.get('social_auth_last_login_backend')

    if not request.user.is_authenticated() and request.GET.get('loggedout') is not None:
        data['statusmessage']='Logout done.'

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

def test(request):
    """ just a test page """
    return render_to_response("scs/test.html", {'ajax':request.is_ajax}, RequestContext(request))

def services(request):
    """ a page with all available applications """
    serviceList = []

    message={}
    if 'delete' in request.GET:
        serviceToDelete=request.GET['delete']
        success = wsdl2mi.DeleteService(serviceToDelete)
        if success[0]:

            message['statusmessage']=success[1]

        else:

            message['errormessage']=success[1]

    if 'wsdlURL' in request.POST:
        wsdlURL=request.POST['wsdlURL']
        try:
            val = URLValidator(verify_exists=False)
            val(wsdlURL)
            success = wsdl2mi.startInstallService(wsdlURL)
            if success[0]:

                message['statusmessage']=success[1]

            else:

                message['errormessage']=success[1]

        except ValidationError, e:
            message['errormessage']="This wsdl URL is not valid"

    for app in settings.INSTALLED_APPS:
        # TODO do a better check
        if app.count('masterinterface') and not app.count('scs') and not app.count('cyfronet'):
            service = app.split('.')[1]
            serviceList.append( service )

    message['services']=serviceList

    return render_to_response("scs/services.html",
            message,
        RequestContext(request))

def contacts(request):
    return render_to_response("scs/contacts.html",
            {},
        RequestContext(request))

def help(request):
    return render_to_response("scs/help.html",
            {},
        RequestContext(request))


def workflows(request):
    return render_to_response("scs/workflows.html",
            {},
        RequestContext(request))

def user_access_admin(request):

    return render_to_response("scs/usersadmin.html",
            {},
        RequestContext(request))