from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from piston.resource import Resource

from views import *
entries = Resource(handler=validate_tkt)
admin.autodiscover()

urlpatterns = patterns(
    'scs_auth.views',
    url(r'^bt_login/$', bt_login , name='bt_login'),
    url(r'^bt_agreement/$', bt_agreement_check, name='bt_agreement'),
    url(r'^bt_loginform/$', bt_loginform , name='bt_loginform'),
    url(r'^auth_login/$', auth_login , name='auth_login'),
    url(r'^auth_loginform/$', auth_loginform , name='auth_loginform'),
    url(r'^done/$', done  , name='done'),
    url(r'^logout/$', logout , name='logout'),
    url(r'^validatetkt/',entries),
    url(r'^validatetkt\.(?P<emitter_format>.+)', entries),
    url(r'^api/validatetkt/',entries),
    url(r'^api/validatetkt\.(?P<emitter_format>.+)', entries),
    url(r'^users_access_search/$', users_access_search , name= 'users_access_search'),
    url(r'^users_update_role_map/$', users_update_role_map ,name= 'users_update_role_map'),
    url(r'^set_security_agent/$', set_security_agent , name= 'set_security_agent'),
    url(r'^users_create_role/$', users_create_role , name='users_create_role'),
    url(r'^users_remove_role/$', users_remove_role , name='users_remove_role'),

)