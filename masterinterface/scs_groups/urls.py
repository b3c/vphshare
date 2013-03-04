__author__ = 'Teo'

from django.conf.urls import patterns, url

from views import  *

urlpatterns = patterns(
    'scs_groups.views',
    url(r'^$', 'list_institutions' ),
    url(r'^subscribe/$', 'subscribe' ),
    url(r'^manage_subscription/$', 'manage_subscription' ),
    url(r'^create_study/$', 'create_study' ),
    url(r'^create_institution/$', 'create_institution' ),
    url(r'^manage_group_request/$', 'manage_group_request' ),
)