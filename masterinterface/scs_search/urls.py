__author__ = ""

from django.conf.urls import patterns, url, include
from views import *
#from piston.resource import Resource

#automatic_search_entries = Resource( handler=AutomaticSearchService)
#guided_search_s1_entries = Resource( handler=GuidedSearchS1Service)
#guided_search_s2_entries = Resource( handler=GuidedSearchS2Service)

urlpatterns = patterns(

    'scs_search.views',
    url( r'^search/$', automaticSearchView , name='automaticSearchView' ),
    url( r'^automatic_search/', automaticSearchService, name='AutomaticSearchService' ) ,
    url( r'^guided_search_s1/', guidedSearchS1Service, name='guidedSearchS1Service' ) ,
    url( r'^guided_search_s2/', guidedSearchS2Service, name='guidedSearchS2Service' ) ,
    )