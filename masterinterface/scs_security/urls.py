__author__ = 'Teo'

from django.conf.urls import patterns, url

from views import *

urlpatterns = patterns(
    'scs_security.views',
    url(r'^$', 'index' ),
    url(r'^policy/$', 'policy' ),
    url(r'^configuration/$', 'configuration'),
    url(r'^deletepolicy/$', 'delete_policy'),
    url(r'^deleteconfiguration/$', 'delete_configuration'),
    url(r'^datashare/$', 'data_share_widget'),
    url(r'^grantrole/$', 'grant_role'),
    url(r'^revokerole/$', 'revoke_role'),
    url(r'^createrole/$', 'create_role')
)