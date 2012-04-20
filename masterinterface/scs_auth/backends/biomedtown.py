"""
BiomedTown OpenID support.

This contribution adds support for BiomedTown OpenID service.
"""

import binascii
from datetime import  datetime
from django.conf import settings
from xmlrpclib import ServerProxy
from django.contrib.auth.backends import RemoteUserBackend
from masterinterface.scs_auth.auth import authenticate
from social_auth.backends import OpenIDBackend, OpenIdAuth, OPENID_ID_FIELD, OLD_AX_ATTRS, AX_SCHEMA_ATTRS, USERNAME, sreg,ax
from openid.consumer.consumer import SUCCESS, CANCEL, FAILURE
from masterinterface.scs_auth.tktauth import *
from django.contrib.auth.models import User
BIOMEDTOWN_URL = 'https://www.biomedtown.org/identity/%s'

PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'masterinterface.scs_auth.auth.userProfileUpdate',
    'masterinterface.scs_auth.auth.socialtktGen',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details',
    )

SREG_ATTR = [
    ('email', 'email'),
    ('fullname', 'fullname'),
    ('nickname', 'nickname'),
    ('country', 'country'),
    ('language', 'language'),
    ('postcode', 'postcode'),
]
class BiomedTownBackend(OpenIDBackend):
    """BiomedTown OpenID authentication backend"""
    name = 'biomedtown'

    def authenticate(self, *args, **kwargs):
        """Authenticate user using social credentials

        Authentication is made if this is the correct backend, backend
        verification is made by kwargs inspection for current backend
        name presence.
        """
        # Validate backend and arguments. Require that the Social Auth
        # response be passed in as a keyword argument, to make sure we
        # don't match the username/password calling conventions of
        # authenticate.
        if not (self.name and kwargs.get(self.name) and 'response' in kwargs):
            return None

        response = kwargs.get('response')
        pipeline = PIPELINE
        kwargs = kwargs.copy()
        kwargs['backend'] = self

        if 'pipeline_index' in kwargs:
            pipeline = pipeline[kwargs['pipeline_index']:]
        else:
            kwargs['details'] = self.get_user_details(response)
            kwargs['uid'] = self.get_user_id(kwargs['details'], response)
            kwargs['is_new'] = False

        out = self.pipeline(pipeline, *args, **kwargs)
        if not isinstance(out, dict):
            return out

        social_user = out.get('social_user')
        if social_user:
            # define user.social_user attribute to track current social
            # account
            user = social_user.user
            user.social_user = social_user
            user.is_new = out.get('is_new')
            return user , out['ticket']

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

    def auth_complete(self, *args, **kwargs):
        """Complete auth process"""
        response = self.consumer().complete(dict(self.data.items()),
            self.request.build_absolute_uri())
        if not response:
            raise ValueError('This is an OpenID relying party endpoint')
        elif response.status == SUCCESS:
            kwargs.update({
                'auth': self,
                'response': response,
                self.AUTH_BACKEND.name: True
            })
            user, tkt64 = authenticate(*args, **kwargs)
            if user:
                self.request.META['VPH_TKT_COOKIE'] = tkt64
                return user
        elif response.status == FAILURE:
            raise ValueError('OpenID authentication failed: %s' %\
                             response.message)
        elif response.status == CANCEL:
            raise ValueError('Authentication cancelled')
        else:
            raise ValueError('Unknown OpenID response type: %r' %\
                             response.status)
    def setup_request(self, extra_params=None):
        """Setup request"""
        openid_request = self.openid_request(extra_params)
        # Request some user details. Use attribute exchange if provider
        # advertises support.
        if openid_request.endpoint.supportsType(ax.AXMessage.ns_uri):
            fetch_request = ax.FetchRequest()
            # Mark all attributes as required, Google ignores optional ones
            for attr, alias in (AX_SCHEMA_ATTRS + OLD_AX_ATTRS):
                fetch_request.add(ax.AttrInfo(attr, alias=alias,
                    required=True))
        else:
            fetch_request = sreg.SRegRequest(optional=dict(SREG_ATTR).keys())
        openid_request.addExtension(fetch_request)

        return openid_request
# Backend definition
BACKENDS = {
    'biomedtown' : BiomedTownAuth,
    }

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
        user.userprofile.country = self.user_dict['country']
        user.userprofile.fullname = self.user_dict['fullname']
        user.userprofile.language = self.user_dict['language']
        user.userprofile.postcode = self.user_dict['postcode']
        user.userprofile.save()
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




