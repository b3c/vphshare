__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'


import requests
import json
from django.conf import settings


SUCCESSFUL_CODES = [200, 201, 204]


def get_securitypolicies(username, ticket):
    """
        return a list of the available policies
    """

    r = requests.get(
        "%s/securitypolicy" % settings.CLOUDFACACE_URL,
        auth=(username, ticket),
        verify=settings.CLOUDFACACE_SSL
    )

    return r.json()


def get_securitypolicy_content(username, ticket, policy_name):
    """
        return the security policy file content
    """

    r = requests.get(
        "%s/securitypolicy/%s/payload" % (settings.CLOUDFACACE_URL, policy_name),
        auth=(username, ticket),
        verify=settings.CLOUDFACACE_SSL
    )

    return r.text


def update_securitypolicy(username, ticket, policy_name, policy_file):
    """
        update the security policy file
    """

    body = json.dumps({'name': policy_name, 'payload': policy_file})

    r = requests.put(
        "%s/securitypolicy/%s" % (settings.CLOUDFACACE_URL, policy_name),
        auth=(username, ticket),
        data = body,
        verify=settings.CLOUDFACACE_SSL
    )

    return r.status_code in SUCCESSFUL_CODES


def create_securitypolicy(username, ticket, policy_name, policy_file):
    """
        create a new security policy file
    """

    body = json.dumps({'name': policy_name, 'payload': policy_file})

    r = requests.post(
        "%s/securitypolicy" % settings.CLOUDFACACE_URL,
        auth=(username, ticket),
        data = body,
        verify=settings.CLOUDFACACE_SSL
    )

    return r.status_code in SUCCESSFUL_CODES


def delete_securitypolicy(username, ticket, policy_name):
    """
        delete an existing security policy
    """

    r = requests.delete(
        "%s/securitypolicy/%s" % (settings.CLOUDFACACE_URL, policy_name),
        auth=(username, ticket),
        verify=settings.CLOUDFACACE_SSL
    )

    return r.status_code in SUCCESSFUL_CODES


def get_securityproxy_configurations(username, ticket):
    """
        return a list of the available policies
    """

    r = requests.get(
        "%s/securityproxy" % settings.CLOUDFACACE_URL,
        auth=(username, ticket),
        verify=settings.CLOUDFACACE_SSL
    )

    return r.json()


def get_securityproxy_configuration_content(username, ticket, configuration_name):
    """
        return the security proxy configuration file content
    """

    r = requests.get(
        "%s/securityproxy/%s/payload" % (settings.CLOUDFACACE_URL, configuration_name),
        auth=(username, ticket),
        verify=settings.CLOUDFACACE_SSL
    )

    return r.text


def create_securityproxy_configuration(username, ticket, configuration_name, configuration_file):
    """
        create a new security proxy configuration
    """

    body = json.dumps({'name': configuration_name, 'payload': configuration_file})

    r = requests.post(
        "%s/securityproxy" % settings.CLOUDFACACE_URL,
        auth=(username, ticket),
        data = body,
        verify=settings.CLOUDFACACE_SSL
    )

    return r.status_code in SUCCESSFUL_CODES


def update_securityproxy_configuration(username, ticket, configuration_name, configuration_file):
    """
        set the security proxy configuration
    """

    body = json.dumps({'name': configuration_name, 'payload': configuration_file})

    r = requests.put(
        "%s/securityproxy/%s" % (settings.CLOUDFACACE_URL, configuration_name),
        auth=(username, ticket),
        data = body,
        verify=settings.CLOUDFACACE_SSL
    )

    return r.status_code in SUCCESSFUL_CODES


def delete_securityproxy_configuration(username, ticket, configuration_name):
    """
        delete an existing security proxy configuration
    """

    r = requests.delete(
        "%s/securityproxy/%s" % (settings.CLOUDFACACE_URL, configuration_name),
        auth=(username, ticket),
        verify=settings.CLOUDFACACE_SSL
    )

    return r.status_code in SUCCESSFUL_CODES


def get_user_resources(username, ticket):
    """
        return available resources in the cloud for the given user
    """

    resources = []

    r = requests.get(
        "%s/workflow/list" % settings.CLOUDFACACE_URL,
        auth=(username, ticket),
        verify=settings.CLOUDFACACE_SSL
    )

    try:
        workflows = r.json()
    except Exception, e:
        workflows = {'workflows': []}

    for wf in workflows['workflows']:
        r = requests.get(
            "%s/workflow/%s" % (settings.CLOUDFACACE_URL, wf['id']),
            auth=(username, ticket),
            verify=settings.CLOUDFACACE_SSL
        )
        workflow = r.json()

        resources.extend(workflow['atomicServiceInstances'])

    return resources
