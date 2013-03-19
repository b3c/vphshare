__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'


import requests
from django.conf import settings


def get_securitypolicies(username, ticket):
    """
        return a list of the available policies
    """

    r = requests.post(
        "%s/securitypolicy" % settings.CLOUDFACACE_URL,
        auth=(username, ticket),
    )

    return r.json()


def get_securitypolicy_file(username, ticket, policy_name):
    """
        return the security policy file content
    """

    r = requests.get(
        "%s/securitypolicy/%s/payload" % (settings.CLOUDFACACE_URL, policy_name),
        auth=(username, ticket),
    )

    return r.text


def set_securitypolicy_file(username, ticket, policy_name, policy_file):
    """
        set the security policy file
    """

    r = requests.post(
        "%s/securitypolicy/%s/payload" % (settings.CLOUDFACACE_URL, policy_name),
        auth=(username, ticket),
        data = {
            'name': policy_name,
            'payload': policy_file
        },
    )

    return True


def get_securityproxy_configuration_file(username, ticket, endpoint):
    """
        return the security proxy configuration file content
    """

    r = requests.get(
        "%s/as/%s/configurations" % (settings.CLOUDFACACE_URL, endpoint),
        auth=(username, ticket),
        data= {
            'load_payload': True
        }
    )

    return r.text


def set_securityproxy_configuration_file(username, ticket, endpoint, configuration_name, configuration_file):
    """
        set the security proxy configuration file
    """

    r = requests.post(
        "%s/as/configurations" % (settings.CLOUDFACACE_URL, endpoint),
        auth=(username, ticket),
        data = {
            'name': configuration_name,
            'payload': configuration_file
        },
    )

    return True


def get_user_resources(username, ticket):
    """
        return available resources in the cloud for the given user
    """

    resources = []

    r = requests.get(
        "%s/workflow/list" % settings.CLOUDFACACE_URL,
        auth=(username, ticket),
    )

    workflows = r.json()

    for wf in workflows['workflows']:
        r = requests.get(
            "%s/workflow/%s" % (settings.CLOUDFACACE_URL, wf['id']),
            auth=(username, ticket)
        )
        workflow = r.json()

        resources.extend(workflow['atomicServiceInstances'])

    return resources
