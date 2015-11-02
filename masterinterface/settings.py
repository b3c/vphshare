# Django settings for vphshare masterinterface project.

import os
from mod_auth import SignedTicket, Ticket

DEBUG = False

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Alfredo Saglimbeni', 'a.saglimbeni@scsitaly.com')
)

# Depending on your configuration this endpoint regards the authentication services located in the folder /authentication
#Follow the readme inside that folder to configure this parameter properly
AUTH_SERVICES = "https://portal.vph-share.eu/api/auth/api"
#Your master interface base URL , all the HTTPRedirect response use this parameter.
BASE_URL = "https://portal.vph-share.eu"
#Where the sessionid is stored in the browser. this support he cros subdomain sessions.
SESSION_COOKIE_DOMAIN = ".vph-share.eu"

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

#By default the master interface use a local sqlite database
#don't use this configuration in production but reconfigure it using local_settings.py
#The sugested database to use in production is Postgres
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PROJECT_ROOT,'vphshare.db'),                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

#Define class where extened user profile most of them come from Biomedtown
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
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'scs.preprocess_middleware.institutionPortaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'scs_auth.preprocess_middleware.masterInterfaceMiddleware',
    'paraviewweb.middleware.paraviewWebMiddleware',
)

ROOT_URLCONF = 'masterinterface.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT,'templates'),
)

#The installed apps of the master interface
#Remeber to add your own apps if it needs.
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    #client for Sentry log manager
    'raven.contrib.django.raven_compat',
    #base application for the biomwedtown auth backend
    'social_auth',
    #base app for the master interface here you can find the base template and the most of the general views.
    'masterinterface.scs',
    #authentication backend
    'masterinterface.scs_auth',
    #Cyfronet filestore and cloufacade
    'masterinterface.cyfronet',
    #semantic search
    'masterinterface.scs_search',
    #django-workflow paket to manage the different status of the sharring request and group mebership request
    'workflows',
    #Initaly used to manage the permission of the master interface not used anymore but left here to avoid conflicts.
    'permissions',
    #Institutrions and vph-share smart group application.
    'masterinterface.scs_groups',
    #Security procy configurator
    'masterinterface.scs_security',
    #Resrouce manager , it works with the metadata repository the core application of the mater interface.
    'masterinterface.scs_resources',
    # the client connentor for the atos services.
    'masterinterface.atos',
    #DB versioning control
    'south',
    #datetime widget for form inputs date type
    'datetimewidget',
    #widget for the select input in the form
    'django_select2',
    #Workspace of the master interface where the user can configure the exectution and run the workflow.
    'masterinterface.scs_workspace',
    #Application that manage the paraviews instances
    'masterinterface.paraviewweb',
    #evolution of the scs_search regard only the refactor of the dataset query_builder.
    'masterinterface.datasets',
    #library for django-celery
    'kombu.transport.django',
    #celery
    'djcelery',
    # color picker widget used in the insitutional portal wizard.
    'paintstore',

    # external jobs
    'masterinterface.cilab_ejobs'
    ##NEW_APP
)


#For the master interface we use the default Bioemdtown backend
#It is an extension od the original openID of social_auth packet
#If you want to use your own identtity provider uncomment what you need bellow
#and configure in according with the django-social-auth packet (see the documentation)
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
    'scs.templates_middleware.get_notifications',
    'scs.templates_middleware.baseurl',
    'scs.templates_middleware.okcookies',
    'templatedomain.domainx' # groups_sites
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
    'disable_existing_loggers': True,
    'root': {
        'level': 'ERROR',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['sentry'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['sentry'],
            'level': 'ERROR',
            'propagate': True,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['sentry'],
            'propagate': True,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['sentry'],
            'propagate': True,
        },
    },
}

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/done'
LOGIN_ERROR_URL = '/login-error/'

#SOCIAL_AUTH SETTINGS
SOCIAL_AUTH_ASSOCIATE_BY_MAIL =True
SOCIAL_AUTH_BACKEND_ERROR_URL = '/scs_auth/bt_loginform/?error=True'
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/scs_auth/bt_loginform/?error=True'
SOCIAL_AUTH_RAISE_EXCEPTIONS = False

# Cyfronet Settings for develop instance use in local_settigs.py this: https://149.156.10.137/api/v1
CLOUDFACACE_URL = "https://vph.cyfronet.pl/api/v1"
CLOUDFACACE_SSL = False

#Atos service
ATOS_SERVICE_URL = "https://149.156.10.131:47056/ex2vtk/?wsdl"

#Ticket expiration timeout in seconds
TICKET_TIMEOUT = 12*60*60  # 12 h

#MOD_AUTH_TKT settings
MOD_AUTH_PUBTICKET = os.path.join(PROJECT_ROOT,'scs_auth/keys/pubkey_DSA.pem')
MOD_AUTH_PRIVTICKET = os.path.join(PROJECT_ROOT,'scs_auth/keys/privkey_DSA.pem')
#MOD_AUTH_PUBTKY COOKIE STYLE
TICKET = SignedTicket(MOD_AUTH_PUBTICKET,MOD_AUTH_PRIVTICKET)

#MOD_AUTH_TKY COOKIE STYLE
#TICKET =  Ticket(SECRET_KEY)

#LOBCDER settings
LOBCDER_HOST = 'lobcder.vph.cyfronet.pl'
LOBCDER_ROOT = '/lobcder/dav'

LOBCDER_WEBDAV_URL = 'https://lobcder.vph.cyfronet.pl/lobcder/dav'
LOBCDER_WEBDAV_HREF = '/lobcder/dav'
LOBCDER_REST_URL = 'https://lobcder.vph.cyfronet.pl/lobcder/rest'
LOBCDER_FOLDER_DOWNLOAD_PATH = '/compress/getzip'

#METADATA SERVICE URL
ATOS_METADATA_URL = 'http://vphshare.atosresearch.eu/metadata-extended'
METADATA_TYPE = ['Dataset', 'File', 'SemanticWebService', 'Workflow', 'AtomicService', 'Workspace']

#WORKFLOW MANAGER URL
WORKFLOW_MANANAGER_URL = 'http://wfmng.vph-share.eu/api'

# federate query end point
FEDERATE_QUERY_URL = 'https://vphsharefind.sheffield.ac.uk/find/VphShareFind.asmx'
FEDERATE_QUERY_SOAP_URL = 'https://share2mdpgateway.sheffield.ac.uk/FederatedQuery'
#PARAVIEWWEB CONFIGS
LOBCDER_DOWNLOAD_DIR = os.path.join(PROJECT_ROOT, 'data_paraview/')
PARAVIEW_HOST = '0.0.0.0:9000'
PARAVIEW_PYTHON_BIN = "/usr/local/lib/paraview-4.0/pvpython"
PARAVIEWWEB_SERVER = os.path.join(PROJECT_ROOT, 'paraviewweb/app/paraviewweb_xmlrpc.py')
PARAVIEWWEB_SERVER_TIMEOUT = 600
PARAVIEWWEB_PORT = 5000

#CELERY CONFIGS
BROKER_URL = 'django://develop'
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERY_DISABLE_RATE_LIMITS = True


#CACHE CONFIGS
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'sharecache',
    }
}

#SENTRY AND RAVEN CONFIGS for Sentry log manager.
RAVEN_CONFIG = {
    'dsn': 'http://2d9a99aec6be407cb4fff11ec2fdf236:86c4c065a476469b9dbf57744e21254a@sentry.vph-share.eu/2',
}

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
