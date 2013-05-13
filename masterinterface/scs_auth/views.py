"""
Scs_auth views contain all frontend views about authentication process.
"""
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout as auth_logout, login
from auth import authenticate
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.utils.datastructures import SortedDict
from django.core.validators import URLValidator

from scs_auth import __version__ as version
from django.conf import settings
from masterinterface.scs.permissions import is_staff
from masterinterface.scs_auth.auth import calculate_sign
import urllib2
import time
from piston.handler import BaseHandler
import os
from M2Crypto import DSA
from permissions.models import Role
from permissions.utils import get_roles, add_role, remove_role
from models import *


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
    context = {'version': version}
    if request.GET.get('error'):
        context['info'] = 'Login Error'
    return render_to_response(
        'scs_auth/bt_loginform.html',
        context,
        RequestContext(request)
    )


def bt_login(request):
    """ return the biomedtown login page with and embedded login iframe"""

    return render_to_response(
        'scs_auth/bt_login.html',
        {'version': version},
        RequestContext(request)
    )


def auth_loginform(request):
    """
    Process login request.
    Create session and user into database if not exist.
    """

    response = {'version': version}
    try:
        if request.method == 'POST' and request.POST.get('biomedtown_username') and request.POST.get(
                'biomedtown_password'):
            username = request.POST['biomedtown_username']
            password = request.POST['biomedtown_password']

            user, tkt64 = authenticate(username=username, password=password)

            if user is not None:

                response['ticket'] = tkt64
                response['last_login'] = 'biomedtown'

                login(request, user)

                response = render_to_response(
                    'scs_auth/done.html',
                    response,
                    RequestContext(request)
                )

                response.set_cookie('vph-tkt', tkt64)

                return response

            else:
                response['info'] = "Username or password not valid."

        elif request.method == 'POST':
            response['info'] = "Login error"
    except:
        response['info'] = "Login error"

    return render_to_response(
        'scs_auth/auth_loginform.html',
        response,
        RequestContext(request)
    )


def auth_done(request, token):
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
    """ return the biomedtown mod_auth tkt login page"""

    return render_to_response('scs_auth/auth_login.html',
                              {'version': version},
                              RequestContext(request)
    )


def logout(request):
    """Logs out user"""
    if request.META.get('HTTP_REFERER'):
        if request.META['HTTP_REFERER'].count('logout') and request.user.is_authenticated():
            return HttpResponseRedirect('http://' + request.META['HTTP_HOST'] + '/')

    auth_logout(request)
    #response = HttpResponseRedirect('http://'+request.META['HTTP_HOST']+'/?loggedout')
    response = render_to_response(
        'scs_auth/logout.html',
        None,
        RequestContext(request)
    )
    response.delete_cookie('vph_cookie')
    return response


class validate_tkt(BaseHandler):
    """
        REST service based on Django-Piston Library.\n
        Now Service support:\n
        # application/json -> http://HOSTvalidatetkt.json?ticket=<ticket>\n
        # text/xml -> http://HOST/validatetkt.xml?ticket=<ticket>\n
        # application/x-yaml -> http://HOST/validatetkt.yaml?ticket=<ticket>\n

        Method validate given ticket, if it valid return User info else 403 error return
    """

    def read(self, request, ticket=''):

        """
            Process a Validate ticket request.
            Arguments:

            request (HTTP request istance): HTTP request send from client.
            ticket (string) : base 64 ticket.

            Return:

            Successes - Json/xml/yaml format response (response format depend on request content/type)
            Failure - 403 error

        """
        try:
            if request.GET.get('ticket'):
                client_address = request.META['REMOTE_ADDR']
                user, tkt64 = authenticate(ticket=request.GET['ticket'], cip=client_address)

                if user is not None:
                    theurl = settings.ATOS_SERVICE_URL
                    username = user.username
                    password = request.GET['ticket']

                    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
                    passman.add_password(None, theurl, username, password)
                    authhandler = urllib2.HTTPBasicAuthHandler(passman)

                    opener = urllib2.build_opener(authhandler)

                    urllib2.install_opener(opener)
                    #pagehandle = urllib2.urlopen(theurl)

                    #if pagehandle.code == 200 :
                    return user.userprofile.to_dict()

            response = HttpResponse(status=403)
            response._is_string = True
            return response
        except Exception, e:
            response = HttpResponse(status=403)
            response._is_string = True
            return response


def validateEmail(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError

    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


@is_staff()
def users_access_search(request):
    Response = {}

    try:
        if request.method == "POST":

            import urllib2

            if not validateEmail(str(request.POST['email'])):
                return HttpResponse('FALSE')

            usermail = str(request.POST['email'])
            f = urllib2.urlopen('https://www.biomedtown.org/getMemberByEmail?email=' + usermail)
            username = f.read()

            if username != '':
                Roles = Role.objects.all()
                try:
                    usersRole, created = User.objects.get_or_create(username=username, email=usermail)
                except:
                    usersRole = {}
                    pass

                resultUsers = {}

                if not isinstance(usersRole, dict):
                    if getattr(resultUsers, usersRole.username, None) is None:
                        resultUsers[usersRole.username] = {}
                        resultUsers[usersRole.username]['email'] = usersRole.email
                    resultUsers[usersRole.username]['roles'] = []
                    for role in get_roles(usersRole):
                        resultUsers[usersRole.username]['roles'].append(role.name)

                #If user is not present into local db
                if username not in resultUsers:
                    resultUsers[username] = {}
                    resultUsers[username]['email'] = usermail
                    resultUsers[username]['roles'] = []
                Response = {'Roles': Roles.values(), 'resultUsers': resultUsers}

                return render_to_response("scs_auth/user_role_search.html",
                                          Response,
                                          RequestContext(request))

            return HttpResponse('FALSE')

    except Exception, e:
        return HttpResponse('FALSE')


@is_staff()
def users_create_role(request):
    try:
        if request.method == "POST":
            if request.POST['role_name'].lower() == "":
                return HttpResponse("FALSE")
            newRole, created = Role.objects.get_or_create(name=request.POST['role_name'].lower())
            if created:
                newRole.save()
            else:
                return HttpResponse("FALSE")
            return HttpResponse('<li id="' + request.POST['role_name'].lower() + '">' + request.POST[
                'role_name'].lower() + ' <input  name="' + request.POST[
                                    'role_name'].lower() + '" type="checkbox" ></li>')

    except  Exception, e:
        return HttpResponse("FALSE")
    return HttpResponse("FALSE")


@is_staff()
def users_remove_role(request):
    try:
        if request.method == "POST" and request.user.is_superuser:
            newRole = Role.objects.get(name=request.POST['role_name'].lower())
            newRole.delete()
            return HttpResponse(request.POST['role_name'].lower())

    except  Exception, e:
        return HttpResponse("FALSE")
    return HttpResponse("FALSE")


@is_staff()
def users_update_role_map(request):
    try:
        if request.method == "POST":
            for key, value in request.POST.iteritems():
                if len(key.split('!')) == 3:
                    userinfo = key.split('!')
                    role = Role.objects.get(name=userinfo[0])
                    if not isinstance(role, Role):
                        return HttpResponse('FALSE')
                    user, created = User.objects.get_or_create(username=userinfo[1], email=userinfo[2])
                    if value == 'on':
                        add_role(user, role)
                    else:
                        remove_role(user, role)

            return HttpResponse('TRUE')
    except Exception, e:
        return HttpResponse("FALSE")

    Roles = Role.objects.all()
    usersRole = User.objects.order_by('username').all()

    resultUsers = SortedDict()
    for i in range(0, len(usersRole.values())):

        if getattr(resultUsers, usersRole[i].username, None) is None:
            resultUsers[usersRole[i].username] = {}
            resultUsers[usersRole[i].username]['email'] = usersRole[i].email
        resultUsers[usersRole[i].username]['roles'] = []
        for role in get_roles(usersRole[i]):
            resultUsers[usersRole[i].username]['roles'].append(role.name)

    return render_to_response("scs_auth/users_role_map.html",
                              {
                                  'Roles': Roles.values(),
                                  'resultUsers': resultUsers,
                                  'request': request
                              },
                              RequestContext(request))


@is_staff()
def set_security_agent(request):
    serviceDIGEST = "user_id=%s&granted_roles=%s&timestamp=%s"
    serviceACTION = "%s/setgrantedroles?%s&sign=%s"
    Roles = ()
    serviceURL = ""
    try:
        if request.method == "POST":
            for key, value in request.POST.iteritems():
                if key == "serviceURL":
                    serviceURL = value
                elif key == "csrfmiddlewaretoken":
                    continue
                else:
                    role = Role.objects.get(name=key)
                    if not isinstance(role, roles):
                        return HttpResponse('FALSE')
                    Roles = Roles + ( key, )

            validator = URLValidator()
            try:
                validator(serviceURL)
            except Exception, e:
                return HttpResponse("Service URL is not well formed")
            granted_roles = ""
            for value in Roles:
                granted_roles += str(value) + ","
            granted_roles = granted_roles[:-1]

            serviceDIGEST = serviceDIGEST % (request.user.username, granted_roles, str(int(time.time())))
            key = DSA.load_key(settings.MOD_AUTH_PRIVTICKET)
            serviceSIGN = calculate_sign(key, serviceDIGEST)

            requestURL = serviceACTION % (serviceURL, serviceDIGEST, serviceSIGN)
            username = "test"
            password = "test"

            passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, requestURL, username, password)
            authhandler = urllib2.HTTPBasicAuthHandler(passman)

            opener = urllib2.build_opener(authhandler)

            urllib2.install_opener(opener)

            try:
                pagehandle = urllib2.urlopen(requestURL)
            except:
                pagehandle = urllib2.urlopen(requestURL)
            if pagehandle.code != 200:
                return HttpResponse(' Sec/Agent request refused.')

            return HttpResponse('TRUE')
    except Exception, e:
        return HttpResponse("FALSE")
