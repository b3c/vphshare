from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from masterinterface.cyfronet import cloudfacade
from permissions.models import Role
import xmltodict
import xml.etree.ElementTree as ET

class SecurityPolicyManager(models.Manager):

    def get(self, ticket, *args, **kwargs):
        policy =  super(SecurityPolicyManager, self).get(*args, **kwargs)
        policy.cloudmetadata = cloudfacade.get_securitypolicy_by_id(ticket, policy.remote_id)
        policy.xacmldict = xmltodict.parse(policy.cloudmetadata['payload'].decode('unicode_escape'))
        policy.policyfile = policy.cloudmetadata['payload'].decode('unicode_escape')
        return policy

    def get_or_create(self, ticket, **kwargs):
        policy, created = super(SecurityPolicyManager,self).get_or_create(**kwargs)
        policy.cloudmetadata = cloudfacade.get_securitypolicy_by_id(ticket, policy.remote_id)
        policy.xacmldict = xmltodict.parse(policy.cloudmetadata['payload'].decode('unicode_escape'))
        policy.policyfile = policy.cloudmetadata['payload'].decode('unicode_escape')
        return policy, created

    def all(self, ticket):
        policies =  super(SecurityPolicyManager, self).all()
        for policy in policies:
            policy.cloudmetadata = cloudfacade.get_securitypolicy_by_id(ticket, policy.remote_id)
            policy.xacmldict = xmltodict.parse(policy.cloudmetadata['payload'].decode('unicode_escape'))
            policy.policyfile = policy.cloudmetadata['payload'].decode('unicode_escape')
        return policies

    def filter(self, ticket, *args, **kwargs):
        policies =  super(SecurityPolicyManager, self).filter(*args, **kwargs)
        for policy in policies:
            policy.cloudmetadata = cloudfacade.get_securitypolicy_by_id(ticket, policy.remote_id)
            policy.xacmldict = xmltodict.parse(policy.cloudmetadata['payload'].decode('unicode_escape'))
            policy.policyfile = policy.cloudmetadata['payload'].decode('unicode_escape')
        return policies

class SecurityPolicy(models.Model):

    remote_id = models.PositiveIntegerField()
    name = models.CharField(max_length=100)
    owner = models.ManyToManyField(User)
    advance_use = models.BooleanField(default=False)

    objects = SecurityPolicyManager()

    def save(self, force_insert=False, force_update=False, using=None, configuration='' , ticket= ''):
        try:
            if ticket and configuration:
                if self.remote_id is None:
                    policy = cloudfacade.create_securitypolicy(ticket, self.name, configuration)
                else:
                    policy = cloudfacade.update_securitypolicy(ticket, self.remote_id, self.name, configuration)
                if 'id' not in policy:
                    return False
                self.remote_id = policy['id']
        except Exception, e:
            raise Exception("Error on secuirty policy role creation")
        super(SecurityPolicy, self).save(force_insert, force_update, using)

    def delete(self, using=None, ticket=''):
        try:
            if ticket:
                if not cloudfacade.delete_securitypolicy(ticket, self.remote_id):
                    return False
            else:
                #I can't delete the policy without ticket
                raise Exception
        except Exception, e:
            raise Exception("Error on secuirty policy role creation")
        super(SecurityPolicy, self).delete(using)

    def parse_xacml(self):
        if hasattr(self,'xacmldict'):
            try:
                xacml = self.cloudmetadata['payload'].decode('unicode_escape')
                root = ET.fromstring(xacml)
                namespace = {"ns":"urn:oasis:names:tc:xacml:2.0:policy:schema:os"}
                data = {}
                #name definition
                data['name'] = root.get('PolicyId')
                #role definition
                if root.find(".//ns:SubjectMatch[@FieldId='role']", namespaces=namespace) is not None:
                    #get role value
                    data['role'] = Role.objects.get(name=root.find(".//ns:SubjectMatch[@FieldId='role']//ns:AttributeValue", namespaces=namespace).text).id
                else:
                    #role is required if not present the policy is not readable by the wizard.
                    raise Exception

                #User data definition
                if root.findall(".//ns:SubjectMatch[@FieldId='udata']", namespaces=namespace):
                    #prepare the three array for the form
                    data['user_attribute_name[0]'] = []
                    data['user_attribute_condition[0]'] = []
                    data['user_attribute_value[0]'] = []
                    #get udata value
                    for udata in root.findall(".//ns:SubjectMatch[@FieldId='udata']", namespaces=namespace):
                        #get the user data field name.
                        udata_field = udata.find('.//ns:SubjectAttributeDesignator', namespaces=namespace).get('AttributeId')
                        #get the user data policy.
                        udata_policy = udata.find('.//ns:AttributeValue', namespaces=namespace).text
                        #extract condition and value.
                        udata_value = ""
                        udata_condition = ""
                        for split in udata_policy.split('*'):
                            if split == '':
                                udata_condition += "*"
                            if split != '':
                                udata_condition += "%s"
                                udata_value = split

                        data['user_attribute_name[0]'].append(udata_field)
                        data['user_attribute_condition[0]'].append(udata_condition)
                        data['user_attribute_value[0]'].append(udata_value)

                # Url contain definition
                if root.find(".//ns:ResourceMatch[@FieldId='urlcontain']", namespaces=namespace) is not None:
                    data['url_contain'] = root.find(".//ns:ResourceMatch[@FieldId='urlcontain']//ns:AttributeValue", namespaces=namespace).text

                #POST parameter definition
                if root.findall(".//ns:ResourceMatch[@FieldId='post']", namespaces=namespace):
                    #prepare the three array for the form
                    data['post_field_name[0]'] = []
                    data['post_field_condition[0]'] = []
                    data['post_field_value[0]'] = []
                    #get udata value
                    for post in root.findall(".//ns:ResourceMatch[@FieldId='post']", namespaces=namespace):
                        #get the user data field name.
                        post_field = post.find('.//ns:ResourceAttributeDesignator', namespaces=namespace).get('AttributeId').replace('POST_','')
                        #get the user data policy.
                        post_policy = post.find('.//ns:AttributeValue', namespaces=namespace).text
                        #extract condition and value.
                        post_value = ""
                        post_condition = ""
                        for split in post_policy.split('*'):
                            if split == '':
                                post_condition += "*"
                            if split != '':
                                post_condition += "%s"
                                post_value = split

                        data['post_field_name[0]'].append(post_field)
                        data['post_field_condition[0]'].append(post_condition)
                        data['post_field_value[0]'].append(post_value)

                # expire date definition
                if root.find(".//ns:Apply[@FieldId='expiry']", namespaces=namespace) is not None:
                    data['expiry_0'] = root.find(".//ns:Apply[@FieldId='expiry']//ns:AttributeValue", namespaces=namespace).text

                # timerange date definition
                if root.find(".//ns:Apply[@FieldId='timerange']", namespaces=namespace) is not None:
                    data['time_start_0'] = root.findall(".//ns:Apply[@FieldId='timerange']//ns:AttributeValue", namespaces=namespace)[0].text
                    data['time_end_0'] = root.findall(".//ns:Apply[@FieldId='timerange']//ns:AttributeValue", namespaces=namespace)[1].text
                return data
            except Exception, e:
                # The xacml file is not readable under the wizard roles
                # use the advance user mode.
                return False
        else:
            return False

class SecurityConfiguration(models.Model):

    remote_id = models.PositiveIntegerField()
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User)
    advance_use = models.BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None, xacml='' , ticket= '',):
        try:
            if ticket and xacml:
                if not cloudfacade.create_securityproxy_configuration(ticket, self.name, xacml):
                    return False
        except Exception, e:
            raise Exception("Error on secuirty policy role creation")
        super(SecurityConfiguration, self).save(force_insert, force_update, using)

    def delete(self, using=None,  ticket=''):
        try:
            if ticket:
                if not cloudfacade.delete_securityproxy_configuration(ticket, self.remote_id):
                    return False
        except Exception, e:
            raise Exception("Error on secuirty policy role creation")
        super(SecurityConfiguration, self).delete(using)

