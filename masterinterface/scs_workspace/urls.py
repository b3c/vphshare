
from django.conf.urls import patterns, url

from views import *

urlpatterns = patterns(
    'scs_resources.views',
    url(r'^workspace/$', workspace, name="workspace"),
    url(r'^workspace/create$', create),
    url(r'^workspace/startTaverna$', startTaverna),
    url(r'^workspace/submitWorkflow$', submitWorkflow),
    url(r'^workspace/startWorkflow$', startWorkflow),
    url(r'^workspace/deleteWorkflow$', deleteWorkflow),
    url(r'^workspace/getExecutionInfo$', getExecutionInfo),
)