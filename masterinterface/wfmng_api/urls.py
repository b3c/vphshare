__author__ = 'Ernesto Coto'
from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.doc import documentation_view

from wfmng_api.handlers import WfMngApiHandler
from piston.handler import BaseHandler

wfmng_api = Resource(handler=WfMngApiHandler)
not_implemented = Resource(handler=BaseHandler)


urlpatterns = patterns('',
    url(r'^$', not_implemented),
    url(r'^wfmng/$', documentation_view),
    url(r'^wfmng/submit/$', wfmng_api),
    url(r'^wfmng/submit$', wfmng_api),
    url(r'^wfmng/(?P<wfrun_id>[^/]+)/$', wfmng_api),
    url(r'^wfmng/(?P<wfrun_id>[^/]+)$', wfmng_api),
)