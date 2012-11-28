__author__ = ""

from django.conf.urls import patterns, url, include
from views import *
from piston.resource import Resource

automatic_search_entries = Resource( handler=AutomaticSearchService)

urlpatterns = patterns(

    'scs_search.views',
    url( r'^search/$', automaticSearchView , name='automaticSearchView' ),
    url( r'^automatic_search/', automatic_search_entries ) ,

    )