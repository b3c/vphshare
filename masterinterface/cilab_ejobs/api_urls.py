__author__ = 'Miguel C.'
from django.conf.urls import patterns, url
from piston.resource import Resource
from masterinterface.cilab_ejobs.api import EJobsAPIHandler


ejobs_api = Resource(handler=EJobsAPIHandler)

urlpatterns = patterns(
    url(r'^ejobs/$', ejobs_api),
    url(r'^ejobs$', ejobs_api),
    url(r'^ejobs/(?P<global_id>[^/]+)/$', ejobs_api),
    url(r'^ejobs/(?P<global_id>[^/]+)$', ejobs_api),
)
