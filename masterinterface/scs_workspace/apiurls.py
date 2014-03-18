__author__ = 'Alfredo Saglimbeni'
from django.conf.urls import patterns, url
from piston.resource import Resource
from masterinterface.scs_workspace.api import workflows_api, WfMngApiHandler


workflows_api_entries = Resource(handler=workflows_api)
wfmng_api = Resource(handler=WfMngApiHandler)

urlpatterns = patterns(
    url(r'^workflows/(?P<global_id>[^/]+)/', workflows_api_entries),
    url(r'^workflows/(?P<global_id>[^/]+)', workflows_api_entries),
    url(r'^workflows', workflows_api_entries),
    url(r'^workflows/', workflows_api_entries),
    url(r'^wfmng/submit/$', wfmng_api),
    url(r'^wfmng/submit$', wfmng_api),
    url(r'^wfmng/(?P<wfrun_id>[^/]+)/$', wfmng_api),
    url(r'^wfmng/(?P<wfrun_id>[^/]+)$', wfmng_api),
    #url(r'^workflows(\.(?P<emitter_format>.+))$', workflows_api_entries),
)
