from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout as auth_logout, login , authenticate
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect

from scs_auth import __version__ as version
from django.conf import settings

import  urllib2

from piston.handler import BaseHandler


def done(request):
    """ login complete view """
    ctx = {
        'version': version,
        'last_login': request.session.get('social_auth_last_login_backend')
    }


    # create ticket

    response = render_to_response(
        'scs_auth/done.html',
        ctx,
        RequestContext(request)
    )



    return response


def bt_loginform(request):
    """ return the biomedtown login form """
    if request.method == 'POST' and request.POST.get('username'):
        name = settings('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY', 'partial_pipeline')
        request.session['saved_username'] = request.POST['username']
        backend = request.session[name]['backend']
        return redirect('socialauth_complete', backend=backend)

    return render_to_response('scs_auth/bt_loginform.html',
            {'version': version},
        RequestContext(request)
    )
def bt_login(request):
    """ return the biomedtown login page with and embedded login iframe"""

    return render_to_response('scs_auth/bt_login.html',
            {'version': version},
        RequestContext(request)
    )

def auth_loginform(request):
    """
    """

    response = {'version': version}

    if request.method == 'POST' and request.POST.get('biomedtown_username') and request.POST.get('biomedtown_password'):
        username=request.POST['biomedtown_username']
        password=request.POST['biomedtown_password']

        user , tkt64 =authenticate(username=username,password=password)


        if user is not None:

            response['ticket']= tkt64
            response['last_login'] ='biomedtown'

            login(request,user)

            response = render_to_response(
                'scs_auth/done.html',
                response,
                RequestContext(request)
            )

            response.set_cookie( 'vph-tkt', tkt64 )

            return response

        else:
            response['info']="Username or password not valid."

    elif request.method == 'POST':
        response['info']="Login error"

    return render_to_response('scs_auth/auth_loginform.html',
        response,
        RequestContext(request)
    )


def auth_done(request,token):
    """ login complete view """
    ctx = {
        'version': version,
        'last_login': "biomedtown"
    }


    response = render_to_response(
        'scs_auth/done.html',
        ctx,
        RequestContext(request)
    )

    return response


def auth_login(request):
    """ return the biomedtown login page with and embedded login iframe"""

    return render_to_response('scs_auth/auth_login.html',
            {'version': version},
        RequestContext(request)
    )

@login_required
def logout(request):
    """Logs out user"""
    if request.META.get('HTTP_REFERER'):
        if request.META['HTTP_REFERER'].count('logout') and request.user.is_authenticated():
            return HttpResponseRedirect('http://'+request.META['HTTP_HOST']+'/')

    auth_logout(request)
    data = {'version': version}
    response = render_to_response(
        'scs/index.html',
        data,
        RequestContext(request)
    )
    response.delete_cookie('vph_cookie')

    return response


class validate_tkt(BaseHandler):


    def read(self, request, ticket=''):
        try:
            if request.GET.get('ticket'):

                user, tkt64 = authenticate(ticket=request.GET['ticket'])

                if user is not None:

                    if user:
                        theurl = settings.ATOS_SERVICE_URL
                        username = user.username
                        password = ticket

                        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
                        passman.add_password(None, theurl, username, password)
                        authhandler = urllib2.HTTPBasicAuthHandler(passman)

                        opener = urllib2.build_opener(authhandler)

                        urllib2.install_opener(opener)
                        pagehandle = urllib2.urlopen(theurl)

                        if pagehandle.code == 200 :
                            return user.get_dict()

            response = HttpResponse(status=403)
            response._is_string = True
            return response
        except Exception, e:
            response = HttpResponse(status=403)
            response._is_string = True
            return response