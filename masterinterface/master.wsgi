import os
import sys

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))

sys.path.append('/scs/app/vphshare')
sys.path.append('/scs/app/vphshare/masterinterface')

os.environ['DJANGO_SETTINGS_MODULE'] = 'masterinterface.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()