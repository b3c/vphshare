"""
    scs_search: urls.py Module
"""
__author__ = ''

from django.conf.urls import patterns, url
from views import *


# EXAMPLE USE WITH DJANGO-PISTON
# from piston.resource import Resource
# automatic_search_entries = Resource( handler=AutomaticSearchService)


urlpatterns = patterns(
    'scs_search.views',

    url(r'^search/free-text/', automatic_search_view, name='automaticSearchView'),

    url(r'^search/complex/latest/', get_latest_query, name='getLatestQuery'),

    url(r'^search/complex/', complex_search_view, name='complexQueryView'),

    url(r'^search/guided/', guided_search_view, name='guidedQueryView'),

    url(r'^automatic_search/', automatic_search_service,
        name='automatic_search_service'),

    url(r'^guided_search_s1/', guided_search_s1_service,
        name='guided_search_s1_service'),

    url(r'^guided_search_s2/', guided_search_s2_service,
        name='guided_search_s2_service'),

    url(r'^guided_search_complex_query/', complex_query_service,
        name='complex_query_service'),

    url(r'^save_complex_query/', save_complex_query,
        name='save_complex_query'),

    url(r'^annotation_search/', annotation_search_service,
        name='annotation_search_service'),

    url(r'^search/$', search_permalink, name="searchPermalink")
    )
