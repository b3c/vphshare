# Django settings for vphshare masterinterface project.

import os
from mod_auth import SignedTicket, Ticket

DEBUG = False

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Matteo Balasso', 'm.balasso@scsitaly.com'),
    ('Alfredo Saglimbeni', 'a.saglimbeni@scsitaly.com')
)

AUTH_SERVICES = "http://auth.biomedtown.org/api"

MANAGERS = ADMINS

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

#DEFAULT_DB = {
#   'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#    'NAME': os.path.join(PROJECT_ROOT, 'vphshare.db'),                      # Or path to database file if using sqlite3.
#    'USER': '',                      # Not used with sqlite3.
#    'PASSWORD': '',                  # Not used with sqlite3.
#    'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
#    'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
#}

# Cyfronet Database
CYFRONET_DB = {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'masterinterface',                      # Or path to database file if using sqlite3.
        'USER': 'vph',                      # Not used with sqlite3.
        'PASSWORD': 'vph123',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'vphsharedb',                      # Or path to database file if using sqlite3.
        'USER': 'vph',                      # Not used with sqlite3.
        'PASSWORD': 'vph.0RG',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

#Define class where extened user profile
AUTH_PROFILE_MODULE = 'scs_auth.UserProfile'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Rome'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT,'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT,'static/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT,'js'),
    os.path.join(PROJECT_ROOT,'img'),
    os.path.join(PROJECT_ROOT,'css'),
    os.path.join(PROJECT_ROOT,'files'),
    os.path.join(PROJECT_ROOT,'media'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '09b63a0aa787db09b73c675b1e04224a'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'scs_auth.preprocess_middleware.masterInterfaceMiddleware'
)

ROOT_URLCONF = 'masterinterface.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT,'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'social_auth',
    'masterinterface.scs',
    'masterinterface.scs_auth',
    'masterinterface.cyfronet',
    'masterinterface.scs_search',
    'workflows',
    'permissions',
    'masterinterface.scs_groups',
    'masterinterface.scs_security',
    'masterinterface.scs_resources',
    'masterinterface.atos',
    'south',
    'datetimewidget',
    'django_select2'

    ##NEW_APP
)

AUTHENTICATION_BACKENDS = (
    'scs_auth.backends.biomedtown.BiomedTownTicketBackend',
    'scs_auth.backends.biomedtown.FromTicketBackend',
    'scs_auth.backends.biomedtown.BiomedTownBackend',
    'django.contrib.auth.backends.ModelBackend',
    #'social_auth.backends.OpenIDBackend',
    #'social_auth.backends.google.GoogleOAuthBackend',
    #'social_auth.backends.google.GoogleOAuth2Backend',
    #'social_auth.backends.google.GoogleBackend',
    )

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'social_auth.context_processors.social_auth_by_name_backends',
    'social_auth.context_processors.social_auth_backends',
    'social_auth.context_processors.social_auth_by_type_backends',
    'scs.templates_middleware.statusMessage',
    'scs.templates_middleware.get_notifications'
    )

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
    )


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'cyfronet': {
            'level': 'DEBUG'
        }
    }
}

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/done'
LOGIN_ERROR_URL = '/login-error/'

#SOCIAL_AUTH SETTINGS
SOCIAL_AUTH_ASSOCIATE_BY_MAIL =True
SOCIAL_AUTH_BACKEND_ERROR_URL = '/scs_auth/bt_loginform/?error=True'
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/scs_auth/bt_loginform/?error=True'
SOCIAL_AUTH_RAISE_EXCEPTIONS = False

# Cyfronet Settings
# CLOUD_PORTLET_LOGIN_URL_TEMPLATE = 'http://vph.cyfronet.pl/puff/portal/clean/default-page-login-clean.psml?user={0}&token={1}&destination={2}'
CLOUD_PORTLET_LOGIN_URL_TEMPLATE = 'http://vph.cyfronet.pl/puff/portal/clean/default-page-login-clean.psml?user={0}&token={1}&destination={2}'
CLOUDFACACE_URL = "http://vph.cyfronet.pl/cloudfacade"
CLOUDFACACE_SSL = False

#Atos service
ATOS_SERVICE_URL = "https://149.156.10.131:47056/ex2vtk/?wsdl"

#Ticket expiration timeout in seconds
TICKET_TIMEOUT = 12*60*60  # 12 h

#MOD_AUTH_TKT settings
MOD_AUTH_PUBTICKET = os.path.join(PROJECT_ROOT,'scs_auth/keys/pubkey_DSA.pem')
MOD_AUTH_PRIVTICKET = os.path.join(PROJECT_ROOT,'scs_auth/keys/privkey_DSA.pem')
#MOD_AUTH_PUBTKY COOKIE STYLE
TICKET =  SignedTicket(MOD_AUTH_PUBTICKET,MOD_AUTH_PRIVTICKET)

#MOD_AUTH_TKY COOKIE STYLE
#TICKET =  Ticket(SECRET_KEY)

#LOBCDER settings
LOBCDER_HOST = '149.156.10.138'
LOBCDER_PORT = 8080
LOBCDER_ROOT = '/lobcder/dav'
LOBCDER_REST = 'http://' + LOBCDER_HOST + ":" + str(LOBCDER_PORT) + "/lobcder/rest"

#PARAVIEW settings
LOBCDER_DOWNLOAD_DIR = os.path.join(PROJECT_ROOT, 'data_paraview/')
PARAVIEW_HOST = '46.105.98.182:9000'

#METADATA SERVICE URL
ATOS_METADATA_URL = 'http://vphshare.atosresearch.eu/metadata-retrieval/rest/metadata'

#WORKFLOW MANAGER URL
WORKFLOW_MANANAGER_URL = 'http://wfmng.vph-share.eu/api'

##################
# LOCAL SETTINGS #
##################

# Allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.
try:
    from local_settings import *
except ImportError:
    pass
