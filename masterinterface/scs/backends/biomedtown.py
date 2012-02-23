"""
BiomedTown OpenID support.

This contribution adds support for BiomedTown OpenID service.
"""
import urlparse

from social_auth.backends import OpenIDBackend, OpenIdAuth, OPENID_ID_FIELD, SREG_ATTR, OLD_AX_ATTRS, AX_SCHEMA_ATTRS, USERNAME

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
                       USERNAME: values.get(USERNAME) or (first_name.title() + last_name.title())})
        return values


class BiomedTownAuth(OpenIdAuth):
    """BiomedTown OpenID authentication"""
    AUTH_BACKEND = BiomedTownBackend

    def openid_url(self):
        """Returns BiomedTown authentication URL"""

        return BIOMEDTOWN_URL % self.data[OPENID_ID_FIELD]


# Backend definition
BACKENDS = {
    'biomedtown': BiomedTownAuth,
    }

