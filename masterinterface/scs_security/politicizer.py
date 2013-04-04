__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'

from lxml import etree


def create_policy_file(actions=[], conditions=[]):
    """
        create a policy file with the given permission
    """

    return "string buffer"


def extract_permission_map(policy_file=""):
    """
        extract permission map from given policy file
    """

    permissions_map = []

    dom = etree.fromstring(policy_file)

    for rule in dom.iterfind(".//Rule"):
        action = rule.find(".//Target//Actions//Action//AttributeValue")
        condition = rule.find(".//Condition//AttributeValue")
        permissions_map.append(
            {'action': action is not None and action.text or '',
             'condition': condition is not None and condition.text or ''}
        )

    return permissions_map

