__author__ = 'Alfredo Saglimbeni (a.saglimbeni@scsitaly.com)'

from django.contrib.auth import get_backends
from django.conf import settings
from django.db.models import ObjectDoesNotExist
from masterinterface.scs_groups.models import VPHShareSmartGroup
from permissions.utils import get_roles
import time
import binascii
import base64
import hashlib
from M2Crypto import RSA, DSA


def authenticate(**credentials):
    """
    Override orginal authenticate to support ticket retrun.
    Now, If the given credentials are valid, return a User object and ticket.
    """
    for backend in get_backends():
        try:
            user = backend.authenticate(**credentials)
        except TypeError:
            # This backend doesn't accept these credentials as arguments. Try the next one.
            continue
        if user is None:
            continue
            # Annotate the user object with the path of the backend.
        if isinstance(user, tuple):
            user[0].backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        else:
            user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        return user


def getUserTokens(user):
    """
    Return the user tokens
    """

    tokens = []

    for role in get_roles(user):
        tokens.append(role.name)

    for group in user.groups.all():

        if hasattr(group,'vphsharesmartgroup'):
            # check if there is a corresponding vphshare group and if it is active
            vphgroup = group.vphsharesmartgroup
            if vphgroup.active:
                tokens.append(group.name)
                #add also the parents
                tokens = set(tokens + vphgroup.get_parents_list_name())
        else:
            # simple group, just add it to the list
            tokens.append(group.name)

    # add default role for all the users
    tokens = set(tokens + ['VPH', 'vph', user.username ])

    return tokens


def userProfileUpdate(details, user, *args, **kwargs):
    """
    New pipeline for Social_auth. It set userProfile attribute.
    """

    if not user:
        return

    change = False
    for key, value in details.items():
        if getattr(user, key, None) is not None:
            change = True
            setattr(user, key, value)
        elif getattr(user.userprofile, key, None) is not None:
            change = True
            setattr(user.userprofile, key, value)
    if change:
        user.userprofile.save()
        user.save()


def socialtktGen(details, user, *args, **kwargs):
    """
    New pipeline for social_auth.
    Generation of ticket from given user details.
    """
    email = details.get('email')

    if email:

        return {'ticket': user.userprofile.get_ticket()}


def calculate_sign(privkey, data):
    """Calculates and returns ticket's signature.

    Arguments:

    ``privkey``:
       Private key object. It must be M2Crypto.RSA.RSA or M2Crypto.DSA.DSA instance.

    ``data``:
       Ticket string without signature part.

    """
    dgst = hashlib.sha1(data).digest()
    if isinstance(privkey, RSA.RSA):
        sig = privkey.sign(dgst, 'sha1')
        sig = base64.b64encode(sig)
    elif isinstance(privkey, DSA.DSA):
        sig = privkey.sign_asn1(dgst)
        sig = base64.b64encode(sig)
    else:
        raise ValueError('Unknonw key type: %s' % privkey)

    return sig