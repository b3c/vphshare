"""
Extend User model with new attribute in user profile.\n
New fields are:\n
        -postcode.\n
        -country.\n
        -fullname.\n
        -language.\n

"""
__author__ = "Alfredo Saglimbeni (a.saglimbeni@scsitaly.com)"

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from permissions.models import Role
from permissions.utils import get_roles


class roles(models.Model):
    id = models.AutoField(primary_key=True)
    roleName = models.CharField(max_length=20, unique=True)


class user_role(models.Model):
    username = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    role = models.ManyToManyField(roles)


class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    postcode = models.CharField(max_length=10, default="")
    country = models.CharField(max_length=20, default="")
    fullname = models.CharField(max_length=30, default="")
    language = models.CharField(max_length=10, default="")
    # roles = models.ManyToManyField(roles)

    def to_dict(self):

        user_key = ['username', 'fullname', 'email', 'language', 'country', 'postcode']

        user_dict = {}

        for i in range(0, len(user_key)):
            if getattr(self, user_key[i], None) is not None:
                user_dict[user_key[i]] = getattr(self, user_key[i])
            else:
                user_dict[user_key[i]] = getattr(self.user, user_key[i])

        user_dict['role'] = [self.user.username]
        for role in get_roles(self.user):
            user_dict['role'].append(role.name)
        for group in self.user.groups.all():
            user_dict['role'].append(group.name)
        return user_dict


class UserAgreement(models.Model):
    user = models.OneToOneField(User)
    cookies = models.BooleanField(null=False, blank=False, default=False)
    privacy = models.BooleanField(null=False, blank=False, default=False)
    ip = models.IPAddressField(null=False)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


post_save.connect(create_user_profile, sender=User)
