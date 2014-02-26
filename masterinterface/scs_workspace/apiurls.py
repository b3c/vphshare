__author__ = 'Alfredo Saglimbeni'
from django.conf.urls import patterns, url
from piston.resource import Resource
from masterinterface.scs_workspace.api import workflows_api


workflows_api_entries = Resource(handler=workflows_api)

urlpatterns = patterns(
    url(r'^workflows/(?P<global_id>[^/]+)/', workflows_api_entries),
    url(r'^workflows/(?P<global_id>[^/]+)', workflows_api_entries),
    url(r'^workflows', workflows_api_entries),
    url(r'^workflows/', workflows_api_entries),
    #url(r'^workflows(\.(?P<emitter_format>.+))$', workflows_api_entries),
)
