__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'


import requests
import json
from django.conf import settings


SUCCESSFUL_CODES = [200, 201, 204]


def get_securitypolicies(ticket):
    """
        return a list of the available policies
    """

    r = requests.get(
        "%s/security_policies" % settings.CLOUDFACACE_URL,
        headers={'MI-TICKET': ticket},
        verify=settings.CLOUDFACACE_SSL
    )
    if r.status_code == 200:
        return eval(r.text)['security_policies']
    return []


def get_securitypolicy_by_id(ticket, policy_id):
    """
        return the security policy file content
    """

    r = requests.get(
        "%s/security_policies?id=%s" % (settings.CLOUDFACACE_URL, policy_id),
        headers={'MI-TICKET': ticket},
        verify=settings.CLOUDFACACE_SSL
    )
    if r.status_code == 200:
        return eval(r.text)['security_policies'][0]
    return None


def update_securitypolicy(ticket, policy_id, policy_name, policy_file):
    """
        update the security policy file
    """

    body = json.dumps({'id': policy_id, 'name': policy_name, 'payload': policy_file})

    r = requests.put(
        "%s/security_policies/%s" % (settings.CLOUDFACACE_URL, policy_id),
        headers={'MI-TICKET': ticket, 'Content-Type': 'application/json'},
        data=body,
        verify=settings.CLOUDFACACE_SSL
    )

    return r.status_code in SUCCESSFUL_CODES


def create_securitypolicy(ticket, policy_name, policy_file):
    """
        create a new security policy file
    """

    body = json.dumps({'name': policy_name, 'payload': policy_file})

    r = requests.post(
        "%s/security_policies" % settings.CLOUDFACACE_URL,
        headers={'MI-TICKET': ticket, 'Content-Type': 'application/json'},
        data = body,
        verify=settings.CLOUDFACACE_SSL
    )

    return r.status_code in SUCCESSFUL_CODES


def delete_securitypolicy(ticket, policy_id):
    """
        delete an existing security policy
    """

    r = requests.delete(
        "%s/security_policies/%s" % (settings.CLOUDFACACE_URL, policy_id),
        headers={'MI-TICKET': ticket},
        verify=settings.CLOUDFACACE_SSL
    )

    return r.status_code in SUCCESSFUL_CODES


def get_securityproxy_configurations(ticket):
    """
        return a list of the available policies
    """

    r = requests.get(
        "%s/security_proxies" % settings.CLOUDFACACE_URL,
        headers={'MI-TICKET': ticket},
        verify=settings.CLOUDFACACE_SSL
    )

    return eval(r.text)['security_proxies']


def get_securityproxy_configurations_by_id(ticket, configuration_id):
    """
        return a list of the available policies
    """

    r = requests.get(
        "%s/security_proxies?id=%s" % (settings.CLOUDFACACE_URL, configuration_id),
        headers={'MI-TICKET': ticket},
        verify=settings.CLOUDFACACE_SSL
    )

    return eval(r.text)['security_proxies'][0]


def get_securityproxy_configuration_content(ticket, configuration_name):
    """
        return the security proxy configuration file content
    """

    r = requests.get(
        "%s/security_proxies/%s/payload" % (settings.CLOUDFACACE_URL, configuration_name),
        headers={'MI-TICKET': ticket},
        verify=settings.CLOUDFACACE_SSL
    )

    return r.text


def create_securityproxy_configuration(ticket, configuration_name, configuration_file):
    """
        create a new security proxy configuration
    """

    body = json.dumps({'name': configuration_name, 'payload': configuration_file})

    r = requests.post(
        "%s/security_proxies" % settings.CLOUDFACACE_URL,
        headers={'MI-TICKET': ticket, 'Content-Type': 'application/json'},
        data=body,
        verify=settings.CLOUDFACACE_SSL
    )

    return r.status_code in SUCCESSFUL_CODES


def update_securityproxy_configuration(ticket, configuration_id, configuration_name, configuration_file):
    """
        set the security proxy configuration
    """

    body = json.dumps({'name': configuration_name, 'payload': configuration_file})

    r = requests.put(
        "%s/security_proxies/%s" % (settings.CLOUDFACACE_URL, configuration_id),
        headers={'MI-TICKET': ticket, 'Content-Type': 'application/json'},
        data = body,
        verify=settings.CLOUDFACACE_SSL
    )

    return r.status_code in SUCCESSFUL_CODES


def delete_securityproxy_configuration(ticket, configuration_id):
    """
        delete an existing security proxy configuration
    """

    r = requests.delete(
        "%s/security_proxies/%s" % (settings.CLOUDFACACE_URL, configuration_id),
        headers={'MI-TICKET': ticket},
        verify=settings.CLOUDFACACE_SSL
    )

    return r.status_code in SUCCESSFUL_CODES

