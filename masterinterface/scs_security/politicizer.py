__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'

from lxml import etree


def create_policy_file(actions=[], conditions=[]):
    """
        create a policy file with the given permission
    """

    # TODO use a sample file here
    sample_policy = """<Policy PolicyId="ExamplePolicy" RuleCombiningAlgId="urn:oasis:names:tc:xacml:1.0:rule-combining-algorithm:permit-overrides"><Target><Subjects><AnySubject/></Subjects><Resources></Resources><Actions><AnyAction/></Actions></Target><Rule RuleId="PermitRole" Effect="Permit"><Target><Subjects><AnySubject/></Subjects><Resources><AnyResource/></Resources><Actions><Action><ActionMatch MatchId="urn:oasis:names:tc:xacml:1.0:function:string-equal"><AttributeValue DataType="http://www.w3.org/2001/XMLSchema#string">read</AttributeValue><ActionAttributeDesignator DataType="http://www.w3.org/2001/XMLSchema#string" AttributeId="urn:oasis:names:tc:xacml:1.0:action:action-id"/></ActionMatch></Action></Actions></Target><Condition FunctionId="urn:oasis:names:tc:xacml:1.0:function:string-equal"><Apply FunctionId="urn:oasis:names:tc:xacml:1.0:function:string-one-and-only"><ResourceAttributeDesignator DataType="http://www.w3.org/2001/XMLSchema#string" AttributeId="role"/></Apply><AttributeValue DataType="http://www.w3.org/2001/XMLSchema#string">VPH</AttributeValue></Condition></Rule></Policy>"""

    dom = etree.fromstring(sample_policy)

    for rule in dom.iterfind(".//Rule"):
        action = rule.find(".//Target//Actions//Action//AttributeValue")
        condition = rule.find(".//Condition//AttributeValue")
        action.text = actions[0]
        condition.text = conditions[0]

    return etree.tostring(dom,pretty_print=True)


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

