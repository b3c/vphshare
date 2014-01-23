
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'vphsharedevdb',                      # Or path to database file if using sqlite3.
        'USER': 'vph',                      # Not used with sqlite3.
        'PASSWORD': 'vph.0RG',                  # Not used with sqlite3.
        'HOST': '46.105.98.182',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

CLOUDFACACE_URL = "http://149.156.10.137/api/v1"
#WORKFLOW MANAGER URL
WORKFLOW_MANANAGER_URL = 'http://devwfmng.vph-share.eu/api'
#PARAVIEW SETTINGS
PARAVIEWWEB_PORT = 5500
