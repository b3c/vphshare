__author__ = 'm.balasso@scsitaly.com'

from masterinterface.scs_resources.models import Resource
from permissions.models import Role, PrincipalRoleRelation
from permissions.utils import has_local_role


def get_resource_local_roles(global_id):

    # TODO HACK! role list is now static :-(

    return Role.objects.filter(name__in=['Reader', 'Editor', 'Manager'])


def get_permissions_map(global_id):
    permissions_map = []
    resource_roles = get_resource_local_roles(global_id)
    resource = Resource.objects.get(global_id=global_id)

    # look for user with those roles
    for role in resource_roles:
        role_relations = PrincipalRoleRelation.objects.filter(role__name__exact=role.name)
        permissions_map.append({
            'name': role.name,
            'groups': [r.group for r in role_relations if r.group is not None and has_local_role(r.group, role, resource)],
            'users': [r.user for r in role_relations if r.user is not None and has_local_role(r.user, role, resource)]
        }
        )

    return permissions_map