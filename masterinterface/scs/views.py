from masterinterface import wsdl2mi
from django.http import HttpResponseRedirect
from django.contrib.auth import logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.messages.api import get_messages
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import string
import ordereddict
from scs import __version__ as version
from permissions.models import Role
from utils import is_staff
from masterinterface import settings
from masterinterface.atos.metadata_connector import *
from masterinterface.scs_resources.utils import get_permissions_map, get_pending_requests_by_user
from django.utils import simplejson
import json
from django.http import HttpResponse


def home(request):
    """Home view """

    data = {'version': version}
    if request.user.is_authenticated():
        data['last_login'] = request.session.get('social_auth_last_login_backend')

        # check if the user has pending requests to process
        pending_requests = get_pending_requests_by_user(request.user)
        if pending_requests:
            data['statusmessage'] = 'Dear %s, you have %s pending request(s) waiting for your action.' % (request.user.first_name, len(pending_requests))

    if not request.user.is_authenticated() and request.GET.get('loggedout') is not None:
        data['statusmessage'] = 'Logout done.'

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


@login_required
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
def test(request):
    """ just a test page """
    return render_to_response("scs/test.html", {'ajax':request.is_ajax}, RequestContext(request))


@login_required
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

    if request.method == 'GET':
        return render_to_response("scs/contacts.html",
            {},
        RequestContext(request))
    else:
        return render_to_response("scs/contacts.html",
                {'statusmessage':'Thanks, your message has been sent!'},
            RequestContext(request))


def help(request):
    return render_to_response("scs/help.html",
            {},
        RequestContext(request))


def data(request):
    return render_to_response("scs/data.html",
        {},
                              RequestContext(request))


def search_data(request):
    return render_to_response("scs/search_data.html",
        {},
                              RequestContext(request))


def upload_data(request):
    return render_to_response("scs/upload_data.html",
        {},
                              RequestContext(request))


@is_staff()
def users_access_admin(request):


    Roles = Role.objects.all()
    return render_to_response("scs/usersadmin.html",
                              {'Roles': Roles.values()},
                              RequestContext(request))


def browse_data_az(request):
    """
        browse data in alphabetical order
    """
    resources_by_letter = {}
    try:
        all_resources = get_all_resources_metadata()
        resources_by_letter = ordereddict.OrderedDict()

        for letter in string.uppercase:
            resources_by_letter[letter] = []

        resources_by_letter['0-9'] = []

        for r in all_resources:
            key = str(r.get('name', ' ')).upper()[0]
            if key in resources_by_letter:
                resources_by_letter[key].append(r)
            else:
                resources_by_letter['0-9'].append(r)
    except Exception, e:
        request.session['errormessage'] = 'Metadata server is down. Please try later'
        pass

    return render_to_response("scs/browseaz.html", {"resources_by_letter": resources_by_letter, "letters": string.uppercase}, RequestContext(request))


## Manage-data modals services ##

@csrf_exempt
def delete_tag_service(request):
    """
        remove tag to resource's metadata
    """
    try:
        if request.method == 'POST':

            removed_tag = request.POST.get('tag', "")
            global_id = request.POST.get('global_id', "")

            metadata = get_resource_metadata(global_id)
            new_tag = {'tags': ''}
            for tag in metadata['tags'].split():
                if tag != removed_tag:
                    new_tag['tags'] += "%s " % tag
            new_tag['tags'] = new_tag['tags'].strip()
            update_resource_metadata(global_id, new_tag)

            response = HttpResponse(status=200)
            response._is_string = True
            return response

        raise

    except Exception, e:
        response = HttpResponse(status=403)
        response._is_string = True
        return response


@csrf_exempt
def add_tag_service(request):
    """
        add tag to resource's metadata
    """
    try:
        if request.method == 'POST':

            added_tag = request.POST.get('tag', "")
            global_id = request.POST.get('global_id', "")

            metadata = get_resource_metadata(global_id)
            if metadata['tags'] is not None:
                for tag in metadata['tags'].split():
                    if tag == added_tag:
                        raise
                new_tags = {'tags': "%s %s" % (metadata['tags'], added_tag)}
            else:
                new_tags = {'tags': added_tag.strip()}
            update_resource_metadata(global_id, new_tags)

            response = HttpResponse(status=200)
            response._is_string = True
            return response

        raise

    except Exception, e:
        response = HttpResponse(status=403)
        response._is_string = True
        return response


@csrf_exempt
def edit_description_service(request):
    """
        add tag to resource's metadata
    """
    from masterinterface.scs_resources.models import Workflow
    try:
        if request.method == 'POST':

            description = request.POST.get('description', "")
            global_id = request.POST.get('global_id', "")
            update_resource_metadata(global_id, {'description': description})

            response = HttpResponse(status=200)
            response._is_string = True
            return response

        raise

    except Exception, e:
        response = HttpResponse(status=403)
        response._is_string = True
        return response

