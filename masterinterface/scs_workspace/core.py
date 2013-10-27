__author__ = 'm.balasso@scsitaly.com'

from xmlrpclib import ServerProxy
from django.conf import settings

WorkflowManager = ServerProxy(settings.WORKFLOW_MANANAGER_URL)
