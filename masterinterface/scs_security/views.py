# Create your views here.

from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from urllib import quote, unquote
from datetime import datetime
from django.contrib.auth.models import User, Group
from django.db.models import ObjectDoesNotExist
from masterinterface.scs_auth.models import UserProfile
from permissions.models import PrincipalRoleRelation, Role
from permissions.utils import add_role, remove_role, has_permission
import json
from lxml import etree
from forms import PropertyForm
from politicizer import create_policy_file, extract_permission_map
from configurationizer import create_configuration_file, extract_configurations
from masterinterface.scs.utils import get_file_data
from masterinterface.cyfronet import cloudfacade
from masterinterface.scs.permissions import is_staff
from masterinterface.atos.metadata_connector import get_resource_metadata


@is_staff()
def index(request):
    """
        security home page
    """

    return render_to_response(
        'scs_security/index.html',
        {'resources': cloudfacade.get_user_resources(request.user.username, request.COOKIES.get('vph-tkt')),
         'policies': cloudfacade.get_securitypolicies(request.user.username, request.COOKIES.get('vph-tkt')),
         'configurations': cloudfacade.get_securityproxy_configurations(request.user.username, request.COOKIES.get('vph-tkt'))},
        RequestContext(request)
    )

@is_staff()
def delete_policy(request):
    """
        delete the policy file
    """

    data = {}

    if request.method == 'POST':
        policy_name = request.POST.get('name')

        if cloudfacade.delete_securitypolicy(request.user.username, request.COOKIES.get('vph-tkt'), policy_name):
            data['statusmessage'] = "Security Policy correctly deleted"

        else:
            data['errormessage'] = "Error while deleting security policy"

    data['policies'] = cloudfacade.get_securitypolicies(request.user.username, request.COOKIES.get('vph-tkt'))

    return render_to_response(
        'scs_security/policy.html',
        data,
        RequestContext(request)
    )

@is_staff()
def policy(request):
    """
        get/set the policy file
    """

    data = {}

    if request.method == 'GET':

        policy_name = request.GET.get('name', '')
        if policy_name:
            policy_file = cloudfacade.get_securitypolicy_content(request.user.username, request.COOKIES.get('vph-tkt'), policy_name)
            permissions_map = extract_permission_map(policy_file)

            data['permissions_map'] = permissions_map
            data['policy_name'] = policy_name
            policy_dom = etree.fromstring(policy_file)
            data['policy_file'] = etree.tostring(policy_dom)

    else:

        policy_name = request.POST['name']

        # create a brand new one by name
        if 'createwithname' in request.POST:
            policy_file = create_policy_file(['read'], [policy_name])

        # update/set with permissions map
        elif 'sumbitwithmap' in request.POST:
            actions = request.POST.getlist('actions', [])
            conditions = request.POST.getlist('conditions', [])
            policy_file = create_policy_file(actions, conditions)

        # update/set by file content
        elif 'sumbitwithcontent' in request.POST:
            policy_file = request.POST.get('filecontent')

        # update/set by file upload
        elif 'sumbitwithfile' in request.POST:
            policy_file = get_file_data(request.FILES.get('fileupload'))

        if "newpolicy" in request.POST:
            if cloudfacade.create_securitypolicy(request.user.username, request.COOKIES.get('vph-tkt'), policy_name, policy_file):
                data['statusmessage'] = "Security Policy file correctly created"
            else:
                data['errormessage'] = "Error while creating security policy"
        else:
            if cloudfacade.update_securitypolicy(request.user.username, request.COOKIES.get('vph-tkt'), policy_name, policy_file):
                data['statusmessage'] = "Security policy correctly updated"
            else:
                data['errormessage'] = "Error while updating security policy"

    data['policies'] = cloudfacade.get_securitypolicies(request.user.username, request.COOKIES.get('vph-tkt'))

    return render_to_response(
        'scs_security/policy.html',
        data,
        RequestContext(request)
    )

@is_staff()
def configuration(request):
    """
        get/set the security proxy configuration
    """

    data = {}

    if request.method == 'GET':

        configuration_name = request.GET.get('name', '')

        if configuration_name:
            data['configuration_name'] = configuration_name
            data['configuration_file'] = cloudfacade.get_securityproxy_configuration_content(request.user.username, request.COOKIES.get('vph-tkt'), configuration_name)
            try:
                data['properties'] = extract_configurations(data['configuration_file'])
            except Exception, e:
                data['properties'] = {}
                data['errormessage'] = "The configuration file loaded seems not to be valid, please upload a new one"

    else:

        configuration_name = request.POST['name']
        # update/set with permissions map
        if 'sumbitwithprops' in request.POST:
            props = {
                'outgoing_port': request.POST.get('outgoing_port', ''),
                'granted_roles': request.POST.get('granted_roles', ''),
                'listening_port': request.POST.get('listening_port', ''),
                'outgoing_address': request.POST.get('outgoing_address', ''),

            }
            configuration_file = create_configuration_file(props)

        # update/set by file content
        elif 'sumbitwithcontent' in request.POST:
            configuration_file = request.POST.get('filecontent')

        # update/set by file upload
        elif 'sumbitwithfile' in request.POST:
            configuration_file = get_file_data(request.FILES.get('fileupload'))

        # check if the file is correct or not
        configuration_file_ok = False
        try:
            extract_configurations(configuration_file)
            configuration_file_ok = True
        except Exception, e:
            configuration_file_ok = False

        if configuration_file_ok:
            if "newconfiguration" in request.POST:
                if cloudfacade.create_securityproxy_configuration(request.user.username, request.COOKIES.get('vph-tkt'), configuration_name, configuration_file):
                    data['statusmessage'] = "Security configuration file correctly created."
                else:
                    data['errormessage'] = "Error while creating security configuration"
            else:
                if cloudfacade.update_securityproxy_configuration(request.user.username, request.COOKIES.get('vph-tkt'), configuration_name, configuration_file):
                    data['statusmessage'] = "Security Proxy configuration correctly updated."
                else:
                    data['errormessage'] = "Error while updating security configuration"
        else:
            data['errormessage'] = "The configuration file uploaded seems not to be valid"

    data['configurations'] = cloudfacade.get_securityproxy_configurations(request.user.username, request.COOKIES.get('vph-tkt'))

    return render_to_response(
        'scs_security/configuration.html',
        data,
        RequestContext(request)
    )


@is_staff()
def delete_configuration(request):
    """
        delete the security proxy configuration file
    """

    data = {}

    if request.method == 'POST':
        configuration_name = request.POST.get('name')

        if cloudfacade.delete_securityproxy_configuration(request.user.username, request.COOKIES.get('vph-tkt'), configuration_name):
            data['statusmessage'] = "Security Proxy configuration correctly deleted"

        else:
            data['errormessage'] = "Error while deleting Security Proxy configuration"

    data['configurations'] = cloudfacade.get_securityproxy_configurations(request.user.username, request.COOKIES.get('vph-tkt'))

    return render_to_response(
        'scs_security/configuration.html',
        data,
        RequestContext(request)
    )


def data_share_widget(request, global_id='f2c84fa7-be6e-4c07-a589-5124066f6425'):
    """
        given a data endpoint display all related information
    """

    # metadata = get_resource_metadata(global_id)

    metadata = {'author': 'mbalasso', 'name': 'Test Resource', 'description': 'test description'}

    # link data to the relative security configuration STATICALLY!
    configuration_name = 'TestMatteo'
    configuration_file = cloudfacade.get_securityproxy_configuration_content(request.user.username, request.COOKIES.get('vph-tkt'), configuration_name)

    # retrieve roles from the configuration
    properties = extract_configurations(configuration_file)

    # look for user with those roles
    role_relations = PrincipalRoleRelation.objects.filter(role__name__exact=properties['granted_roles'])
    groups = [r.group for r in role_relations if r.group is not None]
    users = [r.user for r in role_relations if r.user is not None]

    return render_to_response(
        'scs_security/data_share_widget.html',
        {'tkt64': request.COOKIES.get('vph-tkt'),
         'metadata': metadata,
         'properties': properties,
         'users': users,
         'requests': [],
         'groups': groups},
        RequestContext(request)
    )


def alert_user_by_email(user, resource, action="granted"):
    """
        send an email to alert user
    """


def grant_role(request):
    """
        grant role to user or group
    """

    # if has_permission(request.user, "Manage sharing"):
    name = request.GET.get('name')
    role = Role.objects.get(name=request.GET.get('role'))

    try:
        actor = User.objects.get(username=name)
    except ObjectDoesNotExist, e:
        actor = Group.objects.get(name=name)

    add_role(actor, role)

    response_body = json.dumps({"status": "OK", "message": "Role granted correctly", "alertclass": "alert-success"})
    response = HttpResponse(content=response_body, content_type='application/json')
    return response


def revoke_role(request):
    """
        revoke role from user or group
    """

    # if has_permission(request.user, "Manage sharing"):
    name = request.GET.get('name')
    role = Role.objects.get(name=request.GET.get('role'))

    try:
        actor = User.objects.get(username=name)
    except ObjectDoesNotExist, e:
        actor = Group.objects.get(name=name)

    remove_role(actor, role)

    response_body = json.dumps({"status": "OK", "message": "Role revoked correctly", "alertclass": "alert-success"})
    response = HttpResponse(content=response_body, content_type='application/json')
    return response


def create_role(request):
    """
        create the requested role and the relative security
    """

    # if has_permission(request.user, "Create new role"):
    role_name = request.GET.get('role')
    role, created = Role.objects.get_or_create(name=role_name)
    if not created:
        # role with that name already exists
        response_body = json.dumps({"status": "KO", "message": "Role with name %s already exists" % role_name, "alertclass": "alert-error"})
        response = HttpResponse(content=response_body, content_type='application/json')
        return response

    policy_file = create_policy_file(['read'], [role_name])
    if cloudfacade.create_securitypolicy(request.user.username, request.COOKIES.get('vph-tkt'), role_name, policy_file):
        response_body = json.dumps({"status": "OK", "message": "Role created correctly", "alertclass": "alert-success", "rolename": role_name})
        response = HttpResponse(content=response_body, content_type='application/json')
        return response
    else:
        response_body = json.dumps({"status": "KO", "message": "Interaction with security agent failed", "alertclass": "alert-error"})
        response = HttpResponse(content=response_body, content_type='application/json')
        return response