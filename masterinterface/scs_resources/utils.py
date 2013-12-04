__author__ = 'm.balasso@scsitaly.com'

import random
from django.db.models import Q
from permissions.models import Role, PrincipalRoleRelation
from permissions.utils import has_local_role, has_permission
from workflows.utils import get_state
from masterinterface.scs_resources.config import request_pending
from masterinterface.scs_resources.models import ResourceRequest, Resource
from masterinterface.scs_groups.models import VPHShareSmartGroup


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

    role_relations = PrincipalRoleRelation.objects.filter(
        Q(user=user) | Q(group__in=user.groups.all()),
        role__name__in=['Manager', 'Owner']
    )
    managed_resources = []
    for r in role_relations:
        if r.content is not None and r.content not in managed_resources:
            managed_resources.append(r.content)

    return managed_resources