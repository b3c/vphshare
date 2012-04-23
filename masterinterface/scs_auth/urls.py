from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from piston.resource import Resource
from views import validate_tkt

entries = Resource(handler=validate_tkt)
admin.autodiscover()

urlpatterns = patterns(
    'scs_auth.views',
    url(r'^bt_login/$', 'bt_login'),
    url(r'^bt_loginform/$', 'bt_loginform'),
    url(r'^auth_login/$', 'auth_login'),
    url(r'^auth_loginform/$', 'auth_loginform'),
    url(r'^done/$', 'done'),
    url(r'^logout/$','logout'),
    url(r'^validatetkt/',entries),
    url(r'^validatetkt\.(?P<emitter_format>.+)', entries),
    )