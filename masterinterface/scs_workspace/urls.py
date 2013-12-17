
from django.conf.urls import patterns, url

from views import *

urlpatterns = patterns(
    'scs_resources.views',
    url(r'^workspace/$', workspace, name="workspace"),
    url(r'^workspace/create$', create),
    url(r'^workspace/startExecution$', startExecution),
    url(r'^workspace/deleteExecution$', deleteExecution),
    url(r'^workspace/getExecutionInfo$', getExecutionInfo),
    url(r'^workspace/changestatus$', changeStatus),

)