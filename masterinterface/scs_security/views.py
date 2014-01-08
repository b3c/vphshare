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
from masterinterface.scs.utils import is_staff
from masterinterface.atos.metadata_connector import get_resource_metadata


@is_staff()
def index(request):
    """
        security home page
    """

    return render_to_response(
        'scs_security/index.html',
        {'policies': cloudfacade.get_securitypolicies(request.COOKIES.get('vph-tkt')),
         'configurations': cloudfacade.get_securityproxy_configurations(request.COOKIES.get('vph-tkt'))},
        RequestContext(request)
    )

@is_staff()
def delete_policy(request):
    """
        delete the policy file
    """

    data = {}

    if request.method == 'POST':
        policy_id = request.POST.get('id')

        if cloudfacade.delete_securitypolicy(request.COOKIES.get('vph-tkt'), policy_id):
            data['statusmessage'] = "Security Policy correctly deleted"

        else:
            data['errormessage'] = "Error while deleting security policy"

    data['policies'] = cloudfacade.get_securitypolicies(request.COOKIES.get('vph-tkt'))

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

        policy_id = request.GET.get('id', '')
        if policy_id:
            policy_obj = cloudfacade.get_securitypolicy_by_id(request.COOKIES.get('vph-tkt'), policy_id)
            policy_file = policy_obj['payload'].decode('unicode_escape')
            permissions_map = extract_permission_map(policy_file)
            data['permissions_map'] = permissions_map
            data['policy_obj'] = policy_obj
            policy_dom = etree.fromstring(policy_file)
            data['policy_file'] = etree.tostring(policy_dom)

    elif request.method == 'POST':

        policy_name = request.POST.get('name')
        # create a brand new one by name
        if 'create' in request.POST:

            #policy_file = create_policy_file(['read'], [policy_name])
            if 'fileupload' in request.FILES:
                policy_file = get_file_data(request.FILES.get('fileupload'))
            else:
                policy_file = create_policy_file(['read'], [policy_name])
            if cloudfacade.create_securitypolicy(request.COOKIES.get('vph-tkt'), policy_name, policy_file):
                data['statusmessage'] = "Security Policy file correctly created"
            else:
                data['errormessage'] = "Error while creating security policy"
        # update/set
        else:
            policy_id = request.POST.get('id')
            policy_file = request.POST.get('filecontent')
            if cloudfacade.update_securitypolicy(request.COOKIES.get('vph-tkt'), policy_id, policy_name, policy_file):
                data['statusmessage'] = "Security policy correctly updated"
            else:
                data['errormessage'] = "Error while updating security policy"

        # update/set with permissions map
        #elif 'sumbitwithmap' in request.POST:
        #    actions = request.POST.getlist('actions', [])
        #    conditions = request.POST.getlist('conditions', [])
        #    policy_file = create_policy_file(actions, conditions)

    else:
        raise Exception('method not allowed')

    data['policies'] = cloudfacade.get_securitypolicies(request.COOKIES.get('vph-tkt'))

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

        configuration_id = request.GET.get('id', '')
        if configuration_id:
            configuration_obj = cloudfacade.get_securityproxy_configurations_by_id(request.COOKIES.get('vph-tkt'), configuration_id)
        if configuration_id:
            data['configuration_obj'] = configuration_obj
            data['configuration_file'] = configuration_obj['payload'].decode('unicode_escape')
            try:
                data['properties'] = extract_configurations(data['configuration_file'])
            except Exception, e:
                data['properties'] = {}
                data['errormessage'] = "The configuration file loaded seems not to be valid, please upload a new one"

    else:

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
                if cloudfacade.create_securityproxy_configuration(request.COOKIES.get('vph-tkt'), request.POST['name'], configuration_file):
                    data['statusmessage'] = "Security configuration file correctly created."
                else:
                    data['errormessage'] = "Error while creating security configuration"
            else:
                configuration_id = request.POST['id']
                configuration_obj = cloudfacade.get_securityproxy_configurations_by_id(request.COOKIES.get('vph-tkt'), configuration_id)
                if cloudfacade.update_securityproxy_configuration(request.COOKIES.get('vph-tkt'), configuration_obj['id'], configuration_obj['name'], configuration_file):
                    data['statusmessage'] = "Security Proxy configuration correctly updated."
                else:
                    data['errormessage'] = "Error while updating security configuration"
        else:
            data['errormessage'] = "The configuration file uploaded seems not to be valid"

    data['configurations'] = cloudfacade.get_securityproxy_configurations(request.COOKIES.get('vph-tkt'))

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
        configuration_id = request.POST.get('id')

        if cloudfacade.delete_securityproxy_configuration(request.COOKIES.get('vph-tkt'), configuration_id):
            data['statusmessage'] = "Security Proxy configuration correctly deleted"

        else:
            data['errormessage'] = "Error while deleting Security Proxy configuration"

    data['configurations'] = cloudfacade.get_securityproxy_configurations(request.COOKIES.get('vph-tkt'))

    return render_to_response(
        'scs_security/configuration.html',
        data,
        RequestContext(request)
    )


