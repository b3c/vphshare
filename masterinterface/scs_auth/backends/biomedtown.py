"""
BiomedTown OpenID support.

This contribution adds support for BiomedTown OpenID service.
"""

import binascii
from datetime import  datetime
from django.conf import settings
from xmlrpclib import ServerProxy
from django.contrib.auth.backends import RemoteUserBackend

from django.contrib.auth import authenticate

from social_auth.backends import SocialAuthBackend, BaseAuth, OpenIDBackend, OpenIdAuth, OPENID_ID_FIELD, SREG_ATTR, OLD_AX_ATTRS, AX_SCHEMA_ATTRS, USERNAME
from masterinterface.scs_auth.tktauth import *
from django.contrib.auth.models import User

BIOMEDTOWN_URL = 'https://www.biomedtown.org/identity/%s'



class BiomedTownBackend(OpenIDBackend):
    """BiomedTown OpenID authentication backend"""
    name = 'biomedtown'

    def get_user_details(self, response):
        """Return user details from an OpenID request"""
        values = {USERNAME: '',
                  'email': '',
                  'first_name':'',
                  'last_name':'',
                  'fullname': '',
                  'nickname': '',
                  'postcode': '',
                  'country':'',
                  'language':''}
        # update values using SimpleRegistration or AttributeExchange values
        values.update(self.values_from_response(response,
            SREG_ATTR, OLD_AX_ATTRS + AX_SCHEMA_ATTRS))

        fullname = values.get('fullname') or ''
        first_name = values.get('first_name') or ''
        last_name = values.get('last_name') or ''

        if not fullname and first_name and last_name:
            fullname = first_name + ' ' + last_name
        elif fullname:
            try:  # Try to split name for django user storage
                first_name, last_name = fullname.rsplit(' ', 1)
            except ValueError:
                last_name = fullname

        values.update({'fullname': fullname, 'first_name': first_name,
                       'last_name': last_name,
                       USERNAME: values.get('nickname')})
        return values


class BiomedTownAuth(OpenIdAuth):
    """BiomedTown OpenID authentication"""
    AUTH_BACKEND = BiomedTownBackend

    def openid_url(self):
        """Returns BiomedTown authentication URL"""

        return BIOMEDTOWN_URL % self.data[OPENID_ID_FIELD]


class BiomedTownTicketBackend (RemoteUserBackend):

    service = ServerProxy(settings.AUTH_SERVICES)
    user_dict = {}
    create_unknown_user = True


    def userTicket(self, ticket64):

        ticket= binascii.a2b_base64(ticket64)

        user_data=validateTicket(settings.SECRET_KEY,ticket)
        if user_data:
            # user_key =  ['language', 'country', 'postcode', 'fullname', 'nickname', 'email']
            user_key =  ['nickname', 'fullname', 'email', 'language', 'country', 'postcode']
            user_value=user_data[3]

            self.user_dict={}

            for i in range(0, len(user_key)):
                self.user_dict[user_key[i]]=user_value[i]

            user = None

            if self.create_unknown_user:

                #TODO here we can create a pipeline
                user, created = User.objects.get_or_create(username=self.user_dict['nickname'],email=self.user_dict['email'])

                if created:
                    user = self.configure_user(user)
            else:
                try:
                    user = User.objects.get(email=self.user_dict['email'])
                except User.DoesNotExist:
                    pass


            #### IS NOT A FINAL IMPLEMENTATION ONLY FOR DEVELOPER
            if user.username=='mi_testuser':
                tokens=[]
            else:
                tokens=['developer']
            #######

            new_tkt = createTicket(
                settings.SECRET_KEY,
                self.user_dict['nickname'],
                tokens=tokens,
                user_data=user_value
            )
            tkt64 = binascii.b2a_base64(new_tkt).rstrip()

            return user, tkt64


    def authenticate( self, username = None, password= None):
        """

        """
        if username is None or password is None:
            return None

        try:
            service_response = self.service.rpc_login(username, password)

            if service_response is not False:

                user, tkt64 =self.userTicket(service_response)

                if user is None:
                    return

                return user, tkt64

            return None

        except Exception, e:
            return None

    def configure_user(self, user):

        user.backend ='scs_auth.backend.biomedtowntkt'
        user.first_name = self.user_dict['fullname'].split(" ")[0]
        user.last_name =  self.user_dict['fullname'].split(" ")[1]
        user.email = self.user_dict['email']
        user.last_login = str(datetime.now())

        user.save()

        return user

class FromTicketBackend (BiomedTownTicketBackend):



    def authenticate( self, ticket=None):
        """

        """

        if ticket is None:
            return

        try:

            user, tkt64 =self.userTicket(ticket)

            if user is None:
                return

            return user, tkt64

        except Exception, e:
            return None


# Backend definition
BACKENDS = {
    'biomedtown' : BiomedTownAuth,
    }

