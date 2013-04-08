# Create your views here.

from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from urllib import quote, unquote
from datetime import datetime
import json
from lxml import etree
from forms import PropertyForm
from politicizer import create_policy_file, extract_permission_map
from configurationizer import create_configuration_file, extract_configurations
from masterinterface.scs.utils import get_file_data
from masterinterface.cyfronet import cloudfacade


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


def delete_policy(request):
    """
        delete the policy file
    """

    data = {'policies': cloudfacade.get_securitypolicies(request.user.username, request.COOKIES.get('vph-tkt'))}

    if request.method == 'POST':
        policy_name = request.POST.get('name')

        if cloudfacade.delete_securitypolicy(request.user.username, request.COOKIES.get('vph-tkt'), policy_name):
            data['statusmessage'] = "Security Policy correctly deleted"

        else:
            data['errormessage'] = "Error while deleting security policy"

    return render_to_response(
        'scs_security/policy.html',
        data,
        RequestContext(request)
    )


def policy(request):
    """
        get/set the policy file
    """

    data = {'policies': cloudfacade.get_securitypolicies(request.user.username, request.COOKIES.get('vph-tkt'))}

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
        # update/set with permissions map
        if 'sumbitwithmap' in request.POST:
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

    return render_to_response(
        'scs_security/policy.html',
        data,
        RequestContext(request)
    )


def configuration(request):
    """
        get/set the security proxy configuration
    """

    data = {'configurations': cloudfacade.get_securityproxy_configurations(request.user.username, request.COOKIES.get('vph-tkt'))}

    if request.method == 'GET':

        configuration_name = request.GET.get('name', '')

        if configuration_name:
            data['configuration_name'] = configuration_name
            data['configuration_file'] = cloudfacade.get_securityproxy_configuration_content(request.user.username, request.COOKIES.get('vph-tkt'), configuration_name)
            data['properties'] = extract_configurations(data['configuration_file'])

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

        if "newconfiguration" in request.POST:
            if cloudfacade.create_securityproxy_configuration(request.user.username, request.COOKIES.get('vph-tkt'), configuration_name, configuration_file):
                data['statusmessage'] = "Security configuration file correctly created"
            else:
                data['errormessage'] = "Error while creating security configuration"
        else:
            if cloudfacade.update_securityproxy_configuration(request.user.username, request.COOKIES.get('vph-tkt'), configuration_name, configuration_file):
                data['statusmessage'] = "Security Proxy configuration correctly updated"
            else:
                data['errormessage'] = "Error while updating security configuration"

    return render_to_response(
        'scs_security/configuration.html',
        data,
        RequestContext(request)
    )


def delete_configuration(request):
    """
        delete the security proxy configuration file
    """

    data = {'configurations': cloudfacade.get_securityproxy_configurations(request.user.username, request.COOKIES.get('vph-tkt'))}

    if request.method == 'POST':
        configuration_name = request.POST.get('name')

        if cloudfacade.delete_securityproxy_configuration(request.user.username, request.COOKIES.get('vph-tkt'), configuration_name):
            data['statusmessage'] = "Security Proxy configuration correctly deleted"

        else:
            data['errormessage'] = "Error while deleting Security Proxy configuration"

    return render_to_response(
        'scs_security/configuration.html',
        data,
        RequestContext(request)
    )