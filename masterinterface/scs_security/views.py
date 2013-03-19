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
from forms import PropertyForm
from politicizer import create_policy_file, extract_permission_map
from configurationizer import create_configuration_file, extract_configurations
from masterinterface.cyfronet import cloudfacade


def index(request):
    """
        security home page
    """

    resources = cloudfacade.get_user_resources(request.user.username, request.COOKIES.get('vph-tkt'))

    return render_to_response(
        'scs_security/index.html',
        {'resources': resources},
        RequestContext(request)
    )


def policy(request):
    """
        get/set the policy file
    """

    data = {}

    if request.method == 'GET':

        endpoint = request.GET['endpoint']
        policy_name = request.GET['policy_name']
        policy_file = cloudfacade.get_securitypolicy_file(request.user.username, request.COOKIES.get('vph-tkt'), policy_name)
        permissions_map = extract_permission_map(policy_file)

        data['permissions_map'] = permissions_map
        data['policy_name'] = policy_name

    else:

        endpoint = request.GET['endpoint']
        policy_name = request.POST['policy_name']
        permissions_map = request.POST['permissions']
        policy_file = create_policy_file(permissions_map)

        if cloudfacade.set_securitypolicy_file(request.username, request.COOKIES.get('vph-tkt'), policy_name, policy_file):
            data['statusmessage'] = "Policy file correctly created"

        else:
            data['errormessage'] = "Error while creating policy file"

    return render_to_response(
        'scs_security/policy.html',
        data,
        RequestContext(request)
    )


def securityproxy_configuration(request):
    """
        get/set the properties file
    """

    data = {}

    if request.method == 'GET':

        endpoint = request.GET['endpoint']

        configuration_file = cloudfacade.get_securityproxy_configuration_file(request.user.username, request.COOKIES.get('vph-tkt'), endpoint)
        values = extract_configurations(configuration_file)
        values['configuration_file'] = configuration_file

        data['form'] = PropertyForm(initial=values)

    else:

        form = PropertyForm(request.POST)

        if form.is_valid():

            endpoint = request.GET['endpoint']
            configuration_name = request.POST['configuration_name']
            props = request.POST['configurations']
            configuration_file = create_configuration_file(props)

            if cloudfacade.set_securityproxy_configuration_file(request.username, request.COOKIES.get('vph-tkt'), endpoint, configuration_name, configuration_file):
                data['statusmessage'] = "Property file correctly created"

            else:
                data['errormessage'] = "Error while creating property file"
        else:
            data['form'] = form

    return render_to_response(
        'scs_security/properties.html',
        data,
        RequestContext(request)
    )