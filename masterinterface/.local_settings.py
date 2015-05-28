DEBUG = True

#redefine your local or production database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'vphshare.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

#To use when you are working in your local db
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

#leave Empty if you don't have a log manager Like Sentry.
RAVEN_CONFIG = {

}

#Develpment endpoint for the metadata repository
ATOS_METADATA_URL = 'http://vphshare.atosresearch.eu/metadata-extended-test'
#Develpment endpoint for the cyfronet
CLOUDFACACE_URL = "https://vph-dev.cyfronet.pl/api/v1"
#Develpment endpoint for the cyfronet for the wfmng , if available
WORKFLOW_MANANAGER_URL = 'http://devwfmng.vph-share.eu/api'

