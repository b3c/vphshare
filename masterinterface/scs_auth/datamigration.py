from django.contrib.auth.models import User
from permissions.utils import add_role
from permissions.models import Role
from masterinterface.scs_auth.models import roles

# move all roles to the new model
for role in roles.objects.all():
    new_role, created = Role.objects.get_or_create(name=role.roleName)

for user in User.objects.all():
    for role in user.roles.all():
        add_role(user, role.roleName)

