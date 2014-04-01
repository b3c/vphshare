__author__ = 'm.balasso@scsitaly.com'

import random
from django.db.models import Q, ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from permissions.models import Role, PrincipalRoleRelation
from permissions.utils import has_local_role, has_permission, add_local_role, remove_local_role
from workflows.utils import get_state
from masterinterface.scs_resources.config import request_pending
from masterinterface.scs_resources.models import ResourceRequest, Resource
from masterinterface.scs_groups.models import VPHShareSmartGroup
from django.contrib.contenttypes.models import ContentType

def get_resource_local_roles(resource=None):

    # TODO HACK! role list is now static :-(

    if resource is not None and resource.metadata['type'] and resource.metadata['type'].lower().replace(" ", "") == 'atomicservice':
        return Role.objects.filter(name__in=['Manager', 'Developer', 'Invoker'])
    else:
        return Role.objects.filter(name__in=['Reader', 'Editor', 'Manager'])


def get_resource_global_group_name(resource, local_role_name='read'):
    global_role_name = {'Reader': 'read', 'Editor': 'readwrite', 'Manager': 'admin'}
    return "%s_%s_%s" % (resource.metadata['name'], str(resource.metadata['type']).lower(), global_role_name.get(local_role_name, 'read'))


def get_permissions_map(resource_of_any_type):

    resource = Resource.objects.get(id=resource_of_any_type.id)

    permissions_map = []
    resource_roles = get_resource_local_roles(resource)

    # look for user with those roles
    for role in resource_roles:
        role_relations = PrincipalRoleRelation.objects.filter(role__name__exact=role.name)

        permissions = {
            'name': role.name,
            'groups': [r.group for r in role_relations if r.group is not None and r.content_id == resource.id and has_local_role(r.group, role, resource)],
            'users': [r.user for r in role_relations if r.user is not None and r.content_id == resource.id and has_local_role(r.user, role, resource)]
        }

        for group in permissions['groups']:
            try:
                vph_smart_group = VPHShareSmartGroup.objects.get(name=group.name)
                for user in vph_smart_group.user_set.all():
                    if user not in permissions['users']:
                        permissions['users'].append(user)
                del permissions['groups'][permissions['groups'].index(group)]
            except Exception:
                pass

        permissions_map.append(permissions)

    return permissions_map

def get_user_group_permissions_map(resource_of_any_type):

    if getattr(resource_of_any_type,'resource_ptr', None):
        resource = resource_of_any_type.resource_ptr
        resource.metadata = resource_of_any_type.metadata
    else:
        resource = resource_of_any_type
    permissions_map = []

    ctype = ContentType.objects.get_for_model(resource)
    # look for user with those roles
    role_relations = PrincipalRoleRelation.objects.filter(role__name__in=['Reader', 'Editor', 'Manager'], content_id=resource.id, content_type=ctype)
    for r in role_relations:
        if r.user is not None and r.content_id == resource.id:
            if r.user in permissions_map:
                index = permissions_map.index(r.user)
                if r.role.name not in permissions_map[index].roles:
                    permissions_map[index].roles.append(r.role.name)
            else:
                if getattr(r.user, 'roles', None) is not None:
                    if r.role.name not in r.user.roles:
                        r.user.roles.append(r.role.name)
                else:
                    r.user.roles = []
                    r.user.roles.append(r.role.name)
                permissions_map.append(r.user)
        if r.group is not None and r.content_id == resource.id:

            if resource.metadata['type'] == 'Dataset':
                ##Only for dataset mantain the Woddy approch.
                try:
                    vph_smart_group = VPHShareSmartGroup.objects.get(name=r.group.name)
                    for user in vph_smart_group.user_set.all():
                        if user in permissions_map:
                            index = permissions_map.index(user)
                            if r.role.name not in permissions_map[index].roles:
                                permissions_map[index].roles.append(r.role.name)
                        else:
                            if getattr(user, 'roles', None) is not None:
                                if r.role.name not in user.roles:
                                    user.roles.append(r.role.name)
                            else:
                                user.roles = []
                                user.roles.append(r.role.name)
                            permissions_map.append(user)
                except Exception:
                    if r.group in permissions_map:
                        index = permissions_map.index(r.group)
                        if r.role.name not in permissions_map[index].roles:
                            permissions_map[index].roles.append(r.role.name)
                    else:
                        if getattr(r.group, 'roles', None) is not None:
                            if r.role.name not in r.group.roles:
                                r.group.roles.append(r.role.name)
                        else:
                            r.group.roles = []
                            r.group.roles.append(r.role.name)
                        permissions_map.append(r.group)
                    pass
                ##END - Only for dataset mantain the Woddy approch.
            else:
                if r.group in permissions_map:
                    index = permissions_map.index(r.group)
                    if r.role.name not in permissions_map[index].roles:
                        permissions_map[index].roles.append(r.role.name)
                else:
                    if getattr(r.group, 'roles', None) is not None:
                        if r.role.name not in r.group.roles:
                            r.group.roles.append(r.role.name)
                    else:
                        r.group.roles = []
                        r.group.roles.append(r.role.name)
                    permissions_map.append(r.group)

    return permissions_map

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


def get_pending_requests_by_resource(resource):
    requests = ResourceRequest.objects.filter(resource=resource)
    pending_requests = []
    for r in requests:
        if is_request_pending(r):
            pending_requests.append(r)
    return pending_requests


def susheel_random(digits):
    return '{0}'.format(str(random.randint(0,int("9"*digits))).zfill(digits))


def get_random_citation_link():
    return "".join(['doi:', susheel_random(2), '.', susheel_random(5), '/SHAR', susheel_random(2),'.', susheel_random(4), '.', susheel_random(2)])


def get_managed_resources(user):
    #TODO check all groups hiteracy
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


def grant_permission(name, resource, role):
    try:
        principal = User.objects.get(username=name)
    except ObjectDoesNotExist, e:
        principal = Group.objects.get(name=name)

    if resource.metadata['type'] == 'Dataset':
        try:
        # look for a group with the dataset name
            group_name = get_resource_global_group_name(resource, role)
            group = Group.objects.get(name=group_name)
            if type(principal) is User:
                group.user_set.add(principal)
            group.save()

        except ObjectDoesNotExist, e:
            # global_role, created = Role.objects.get_or_create(name="%s_%s" % (resource.globa_id, role.name))
            #add_role(principal, global_role)
            pass

            # grant local role to the user

    add_local_role(resource, principal, role)

    return principal