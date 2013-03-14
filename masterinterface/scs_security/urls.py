__author__ = 'Teo'

from django.conf.urls import patterns, url

from views import *

urlpatterns = patterns(
    'scs_security.views',
    url(r'^$', 'index' ),
    url(r'^policy/$', 'policy' ),
    url(r'^properties/$', 'properties' ),
)