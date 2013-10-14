__author__ = 'Alfredo Saglimbeni <a.saglimbeni@scsitaly.com>'


from django.conf.urls import patterns, url
from piston.resource import Resource
from masterinterface.scs.api import Notify

notify_entries = Resource(handler=Notify)

urlpatterns = patterns(
    url(r'^notify', notify_entries),
    url(r'^notify/', notify_entries),
    url(r'^notify\.(?P<emitter_format>.+)', notify_entries),

)