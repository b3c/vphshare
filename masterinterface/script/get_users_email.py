import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

sys.path.append(PROJECT_ROOT)
sys.path.append( os.path.split(PROJECT_ROOT)[0] )

os.environ['DJANGO_SETTINGS_MODULE'] = 'masterinterface.settings'

from django.contrib.auth.models import User
us = User.objects.all()
for u in us:
 print "%s ," % u.email


