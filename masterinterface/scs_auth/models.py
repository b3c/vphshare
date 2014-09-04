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
from django.conf import settings
from scs_auth.auth import getUserTokens
import time
import binascii

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
    privacy = models.BooleanField(default=False)
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

        # add default role for all the users
        if not user_dict['role'].count("VPH"):
            user_dict['role'].append("VPH")
        return user_dict

    def get_ticket(self, expire_time = None):
        """
            return the ticket of the user
        """

        user_value = [ self.user.username, self.fullname, self.user.email, self.language, self.country, self.postcode]

        user = self.user
        tokens = getUserTokens(user)

        if expire_time is None:
            validuntil = settings.TICKET_TIMEOUT + int(time.time())
        else:
            validuntil = expire_time * 86400 + int(time.time())

        ticketObj = settings.TICKET
        try:
            new_tkt = ticketObj.createTkt(
                user.username,
                tokens=tokens,
                user_data=user_value,
                #user_data=[],
                #cip = kwargs['request'].META['REMOTE_ADDR'],
                validuntil=validuntil,
                encoding='utf-8'
            )
        except  Exception, e:
            print e

        tkt64 = binascii.b2a_base64(new_tkt).rstrip()

        return tkt64


class UserAgreement(models.Model):
    user = models.OneToOneField(User)
    cookies = models.BooleanField(null=False, blank=False, default=False)
    privacy = models.BooleanField(null=False, blank=False, default=False)
    ip = models.IPAddressField(null=False, default='0.0.0.0')

    def __unicode__(self):
        return unicode(self.user)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


post_save.connect(create_user_profile, sender=User)
