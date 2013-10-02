__author__ = 'Alfredo Saglimbeni <a.saglimbeni@scsitaly.com>'


from django.conf.urls import patterns, url
from piston.resource import Resource
from api import *

notify_entries = Resource(handler=notify)

urlpatterns = patterns(
    url(r'^notify/', notify_entries),

)