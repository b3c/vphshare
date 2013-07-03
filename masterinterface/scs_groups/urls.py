__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'

from django.conf.urls import patterns, url
from scs_groups.views import *

urlpatterns = patterns(
    'scs_groups.views',

    url(r'^(?P<idGroup>\d+)/$', 'group_details'),
    url(r'^(?P<idGroup>\d+)/(?P<idStudy>\d+)/$', 'group_details'),

    #subscription to group
    url(r'^(?P<idGroup>\d+)/subscribe/$', 'subscribe'),
    url(r'^(?P<idGroup>\d+)/(?P<iduser>\d+)/subscribe/$', 'subscribe'),
    url(r'^(?P<idGroup>\d+)/(?P<iduser>\d+)/unsubscribe/$', 'unsubscribe'),
    url(r'^(?P<idGroup>\d+)/addtogroup/$', 'add_to_group'),

    #subscription to study
    url(r'^(?P<idGroup>\d+)/(?P<idStudy>\d+)/studysubscribe/$', 'subscribe'),
    url(r'^(?P<idGroup>\d+)/(?P<idStudy>\d+)/(?P<iduser>\d+)/subscribe/$', 'subscribe'),
    url(r'^(?P<idGroup>\d+)/(?P<idStudy>\d+)/(?P<iduser>\d+)/unsubscribe/$', 'unsubscribe'),
    url(r'^(?P<idGroup>\d+)/(?P<idStudy>\d+)/addtogroup/$', 'add_to_group'),


    url(r'^subscribe/$', 'subscribe'),
    url(r'^create_study/$', 'create_study'),
    url(r'^create_institution/$', 'create_institution'),
    url(r'^manage_group_request/$', 'manage_group_request'),
    url(r'^api/$', 'api_help'),

    url(r'^$', 'group_details'),

)
