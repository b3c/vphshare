__author__ = 'm.balasso@scsitaly.com'

from xmlrpclib import ServerProxy

wfmng = ServerProxy(settings['WORKFLOW_MANANAGER_URL'])
