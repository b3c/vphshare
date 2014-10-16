__author__ = 'm.balasso@scsitaly.com'

from django.db.models import Q, ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from permissions.models import Role, PrincipalRoleRelation
from workflows.utils import get_state
from masterinterface.scs_resources.config import request_pending


def remove_local_role(obj, principal, role):
    """Removes role from obj and principle.

    **Parameters:**

    obj
        The object from which the role is removed.

    principal
        The principal (user or group) from which the role is removed.

    role
        The role which is removed.
    """
    try:
        ctype = ContentType.objects.get_for_model(obj)

        if isinstance(principal, User):
            ppr = PrincipalRoleRelation.objects.get(
                user=principal, role=role, content_id=obj.id, content_type=ctype)
        elif principal is None :
            ppr = PrincipalRoleRelation.objects.get(
                user=principal, group=principal, role=role, content_id=obj.id, content_type=ctype)
        else:
            ppr = PrincipalRoleRelation.objects.get(
                group=principal, role=role, content_id=obj.id, content_type=ctype)

    except PrincipalRoleRelation.DoesNotExist:
        return False
    else:
        ppr.delete()

    return True

def add_local_role(obj, principal, role):
    """Adds a local role to a principal.

    **Parameters:**

    obj
        The object for which the principal gets the role.

    principal
        The principal (user or group) which gets the role.

    role
        The role which is assigned.
    """
    ctype = ContentType.objects.get_for_model(obj)
    if isinstance(principal, User):
        try:
            ppr = PrincipalRoleRelation.objects.get(user=principal, role=role, content_id=obj.id, content_type=ctype)
        except PrincipalRoleRelation.DoesNotExist:
            PrincipalRoleRelation.objects.create(user=principal, role=role, content=obj)
            return True
    elif principal is None:
        try:
            ppr = PrincipalRoleRelation.objects.get(user=principal, group=principal, role=role, content_id=obj.id, content_type=ctype)
        except PrincipalRoleRelation.DoesNotExist:
            PrincipalRoleRelation.objects.create(user=principal, group=None, role=role, content=obj)
            return True
    else:
        try:
            ppr = PrincipalRoleRelation.objects.get(group=principal, role=role, content_id=obj.id, content_type=ctype)
        except PrincipalRoleRelation.DoesNotExist:
            PrincipalRoleRelation.objects.create(group=principal, role=role, content=obj)
            return True

    return False

def get_resource_local_roles(resource=None):

    return Role.objects.filter(name__in=['Reader', 'Editor', 'Manager'])

def get_resource_global_group_name(resource, local_role_name='read'):
    global_role_name = {'Reader': 'read', 'Editor': 'readwrite', 'Manager': 'admin'}
    return "%s_%s_%s" % (resource.metadata['name'], str(resource.metadata['type']).lower(), global_role_name.get(local_role_name, 'read'))

def is_request_pending(r):
    state = get_state(r)
    if state.name == request_pending.name:
        return True

def get_readable_resources(user):
    readable_resource_ids = set(PrincipalRoleRelation.objects.filter(Q(user=user) | Q(group__in=user.groups.all()) | Q(user=None, group=None), role__name__in=['Reader', 'Editor', 'Manager','Owner']    ).exclude( content_id=None, content_type=None).values_list('content_id',flat=True))
    return readable_resource_ids

def get_editable_resources(user):
    editable_resource_ids = set(PrincipalRoleRelation.objects.filter(Q(user=user) | Q(group__in=user.groups.all()) | Q(user=None, group=None), role__name__in=['Editor', 'Manager', 'Owner']).exclude( content_id=None, content_type=None).values_list('content_id',flat=True))
    return editable_resource_ids

def get_managed_resources(user):
    managed_resource_ids = set(PrincipalRoleRelation.objects.filter(Q(user=user) | Q(group__in=user.groups.all()) | Q(user=None, group=None), role__name__in=['Manager', 'Owner']).exclude( content_id=None, content_type=None).values_list('content_id',flat=True))
    return managed_resource_ids


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
    if resource.metadata['type'] == 'File' and ticket:
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
            elif not isinstance(permissions['permissions'][permission_match], list) and permissions['permissions'][permission_match] != name:
                permissions['permissions'][permission_match] = [permissions['permissions'][permission_match], name]
        result = requests.put('%s/item/permissions/%s' % (settings.LOBCDER_REST_URL, resource.metadata['localID']), auth=('admin', ticket), verify=False, data=xmltodict.unparse(permissions),  headers = {'content-type': 'application/xml'})
        if result.status_code not in [204,201,200]:
            raise Exception('LOBCDER permision set error')
    #end lobcder repository update

    add_local_role(resource, principal, role)

    return principal


def revoke_permision(name, resource, role, ticket=None):
    if name is not None:
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
    else:
        principal = None

    remove_local_role(resource, principal, role)

    if resource.metadata['type'] == 'File' and ticket:
        import requests
        import xmltodict
        from django.conf import settings
        permission_map = resource.get_user_group_permissions_map()
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
            if permissions['permissions'].get(permission_match, None) is not None and principal is not None:
                assigned_roles = permission_map[permission_map.index(principal)].roles if principal in permission_map else []
                if isinstance(permissions['permissions'][permission_match], list):
                    index = permissions['permissions'][permission_match].index(name)
                    if 'Manager' not in assigned_roles:
                        if ('Reader' not in assigned_roles and permission_match is 'read') or ('Editor' not in assigned_roles and permission_match is 'write'):
                            del permissions['permissions'][permission_match][index]
                else:
                    if 'Manager' not in assigned_roles:
                        if ('Reader' not in assigned_roles and permission_match is 'read') or ('Editor' not in assigned_roles and permission_match is 'write'):
                            del permissions['permissions'][permission_match]
            elif permissions['permissions'].get(permission_match, None) is not None and principal is None:
                if isinstance(permissions['permissions'][permission_match], list) and name in permissions['permissions'][permission_match]:
                    index = permissions['permissions'][permission_match].index(name)
                    del permissions['permissions'][permission_match][index]
                elif permissions['permissions'][permission_match] == name:
                    del permissions['permissions'][permission_match]

        result = requests.put('%s/item/permissions/%s' % (settings.LOBCDER_REST_URL,resource.metadata['localID']), auth=('admin', ticket), data=xmltodict.unparse(permissions), verify=False, headers = {'content-type': 'application/xml'})
        if result.status_code not in [204,201,200]:
            raise Exception('LOBCDER permision set error')
    return True