
from django.conf.urls import patterns, url

from views import *

urlpatterns = patterns(
    'scs_resources.views',
    url(r'^workspace/$', workspace),
    url(r'^workspace/create$', create),
    url(r'^workspace/taverna/$', starttaverna),
    url(r'^workspace/submit/$', submit),
    url(r'^workspace/executions/(?P<workflow_id>\d+)/start$', start),
)