__author__ = 'Teo'

from django.conf.urls import patterns, url

from views import  *

urlpatterns = patterns(
    'scs_groups.views',
    url(r'^$', 'list_institutions' ),
    url(r'^subscribe_to_institution/$', 'subscribe_to_institution' ),
    url(r'^manage_subscription/$', 'manage_subscription' )
)