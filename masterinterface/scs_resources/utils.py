__author__ = 'm.balasso@scsitaly.com'

from django.db.models import Q, ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from permissions.models import Role, PrincipalRoleRelation
from permissions.utils import has_local_role, has_permission, add_local_role, remove_local_role
from workflows.utils import get_state
from masterinterface.scs_resources.config import request_pending
from masterinterface.scs_resources.models import ResourceRequest

def get_resource_local_roles(resource=None):

    return Role.objects.filter(name__in=['Reader', 'Editor', 'Manager'])

def get_resource_global_group_name(resource, local_role_name='read'):
    global_role_name = {'Reader': 'read', 'Editor': 'readwrite', 'Manager': 'admin'}
    return "%s_%s_%s" % (resource.metadata['name'], str(resource.metadata['type']).lower(), global_role_name.get(local_role_name, 'read'))

def is_request_pending(r):
    state = get_state(r)
    if state.name == request_pending.name:
        return True


def get_pending_requests_by_user(user):
    requests = ResourceRequest.objects.filter(resource__owner=user)
    pending_requests = []
    for r in requests:
        if is_request_pending(r):
            pending_requests.append(r)
    return pending_requests

def get_readable_resources(user):
    role_relations = PrincipalRoleRelation.objects.filter(
        Q(user=user) | Q(group__in=user.groups.all()) | Q(user=None, group=None),
        role__name__in=['Reader', 'Editor', 'Manager']
    ).exclude( content_id=None, content_type=None)
    managed_resources = []
    for r in role_relations:
        if r.content is not None and r.content not in managed_resources:
            if PrincipalRoleRelation.objects.filter(Q(user=user), role__name='Owner', content_id= r.content_id).count() == 0:
                managed_resources.append(r.content)

    return managed_resources

def get_editable_resources(user):
    role_relations = PrincipalRoleRelation.objects.filter(
        Q(user=user) | Q(group__in=user.groups.all()),
        role__name__in=['Editor', 'Manager']
    ).exclude( content_id=None, content_type=None)
    managed_resources = []
    for r in role_relations:
        if r.content is not None and r.content not in managed_resources:
            if PrincipalRoleRelation.objects.filter(Q(user=user), role__name='Owner', content_id= r.content_id).count() == 0:
                managed_resources.append(r.content)

    return managed_resources

def get_managed_resources(user):
    role_relations = PrincipalRoleRelation.objects.filter(
        Q(user=user) | Q(group__in=user.groups.all()),
        role__name__in=['Manager']
    ).exclude( content_id=None, content_type=None)
    managed_resources = []
    for r in role_relations:
        if r.content is not None and r.content not in managed_resources:
            if PrincipalRoleRelation.objects.filter(Q(user=user), role__name='Owner', content_id= r.content_id).count() == 0:
                managed_resources.append(r.content)

    return managed_resources


def alert_user_by_email(mail_from, mail_to, subject, mail_template, dictionary={}):
    """
        send an email to alert user
    """

    text_content = loader.render_to_string('scs_resources/%s.txt' % mail_template, dictionary=dictionary)
    html_content = loader.render_to_string('scs_resources/%s.html' % mail_template, dictionary=dictionary)
    msg = EmailMultiAlternatives(subject, text_content, mail_from, [mail_to])
    msg.attach_alternative(html_content, "text/html")
    msg.content_subtype = "html"
    msg.send()

#TODO create the complementary method revoke_permision.
def grant_permission(name, resource, role, ticket=None):
    if name is not None:
        try:
            principal = User.objects.get(username=name)
        except ObjectDoesNotExist, e:
            principal = Group.objects.get(name=name)

        if resource.metadata['type'] == 'Dataset':
            try:
            # look for a group with the dataset name
                group_name = get_resource_global_group_name(resource, role.name)
                group = Group.objects.get(name=group_name)
                if type(principal) is User:
                    group.user_set.add(principal)
                group.save()

            except ObjectDoesNotExist, e:
                # global_role, created = Role.objects.get_or_create(name="%s_%s" % (resource.globa_id, role.name))
                #add_role(principal, global_role)
                pass

                # grant local role to the user
    else:
        principal = None

    #set the role for files in lobcder repository
    if resource.metadata['type'] == 'File':
        import requests
        import xmltodict
        from django.conf import settings
        permissions = xmltodict.parse(requests.get('%s/item/permissions/%s' % (settings.LOBCDER_REST_URL,resource.metadata['localID']), auth=('admin', ticket), verify=False).text)
        file_permissions_match = {'Reader':['read'],'Editor':['write'], 'Manager':['write','read'], 'Owner':['owner']}
        if principal is None:
            # set the role to all users, vph is the default group for all users in vph-share
            name = 'vph'
        else:
            name = getattr(principal,'username',getattr(principal,'name',None))
        if settings.DEBUG:
                name = name+"_dev"
        for permission_match in file_permissions_match[role.name]:
            if permissions['permissions'].get(permission_match, None) is None:
                permissions['permissions'][permission_match] = [name]
            elif isinstance(permissions['permissions'][permission_match], list) and name not in permissions['permissions'][permission_match]:
                permissions['permissions'][permission_match] += [name]
            elif permissions['permissions'][permission_match] != name:
                permissions['permissions'][permission_match] = [permissions['permissions'][permission_match], name]

        result = requests.put('%s/item/permissions/%s' % (settings.LOBCDER_REST_URL, resource.metadata['localID']), auth=('admin', ticket), verify=False, data=xmltodict.unparse(permissions),  headers = {'content-type': 'application/xml'})
        if result.status_code not in [204,201,200]:
            raise Exception('LOBCDER permision set error')
    #end lobcder repository update

    add_local_role(resource, principal, role)

    return principal


def revoke_permision(name, resource, role, ticket=None):
    try:
        principal = User.objects.get(username=name)
    except ObjectDoesNotExist, e:
        principal = Group.objects.get(name=name)

    try:
        # look for a group with the dataset name
        group_name = get_resource_global_group_name(resource, role.name)
        group = Group.objects.get(name=group_name)
        if type(principal) is User:
            group.user_set.remove(principal)
        group.save()

    except ObjectDoesNotExist, e:
        # TODO REMOVE GLOBAL ROLE ACCORDING TO RESOURCE NAME!!! and update the security proxy?
        # global_role, created = Role.objects.get_or_create(name="%s_%s" % (resource.globa_id, role.name))
        # remove_role(principal, global_role)
        pass
    if resource.metadata['type'] == 'File':
        import requests
        import xmltodict
        from django.conf import settings
        permissions = xmltodict.parse(requests.get('%s/item/permissions/%s' % (settings.LOBCDER_REST_URL,resource.metadata['localID']), auth=('admin', ticket), verify=False).text)
        file_permissions_match = {'Reader':'read','Editor':'write', 'Manager':'owner', 'Ownser':'owner'}

        if settings.DEBUG:
            name = name+"_dev"
        if permissions['permissions'].get(file_permissions_match[role.name], None) is not None:
            if isinstance(permissions['permissions'][file_permissions_match[role.name]], list):
                index = permissions['permissions'][file_permissions_match[role.name]].index(name)
                del permissions['permissions'][file_permissions_match[role.name]][index]
            else:
                del permissions['permissions'][file_permissions_match[role.name]]

            result = requests.put('%s/item/permissions/%s' % (settings.LOBCDER_REST_URL,resource.metadata['localID']), auth=('admin', ticket), data=xmltodict.unparse(permissions), verify=False, headers = {'content-type': 'application/xml'})
            if result.status_code not in [204,201,200]:
                raise Exception('LOBCDER permision set error')

    remove_local_role(resource, principal, role)

    return True