"""
BiomedTown OpenID support.

This contribution adds support for BiomedTown OpenID service.
"""
import urlparse

from social_auth.backends import OpenIDBackend, OpenIdAuth, OPENID_ID_FIELD

BIOMEDTOWN_URL = 'https://www.biomedtown.org/identity/%s'


class BiomedTownBackend(OpenIDBackend):
    """BiomedTown OpenID authentication backend"""
    name = 'biomedtown'


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

