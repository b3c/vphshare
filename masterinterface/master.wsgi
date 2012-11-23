import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

sys.path.append(PROJECT_ROOT)
sys.path.append( os.path.split(PROJECT_ROOT)[0] )

os.environ['DJANGO_SETTINGS_MODULE'] = 'masterinterface.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()