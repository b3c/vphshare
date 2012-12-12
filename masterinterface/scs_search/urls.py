"""
    scs_search: urls.py Module
"""
__author__ = ''

from django.conf.urls import patterns, url
from views import automatic_search_view, automatic_search_service, \
    guided_search_s1_service, guided_search_s2_service, complex_query_service


# EXAMPLE USE WITH DJANGO-PISTON
# from piston.resource import Resource
# automatic_search_entries = Resource( handler=AutomaticSearchService)


urlpatterns = patterns(
    'scs_search.views',

    url(r'^search/$', automatic_search_view, name='automaticSearchView'),

    url(r'^automatic_search/', automatic_search_service,
        name='automatic_search_service'),

    url(r'^guided_search_s1/', guided_search_s1_service,
        name='guided_search_s1_service'),

    url(r'^guided_search_s2/', guided_search_s2_service,
        name='guided_search_s2_service'),

    url(r'^guided_search_complex_query/',
        complex_query_service,
        name='complex_query_service'),
    )
