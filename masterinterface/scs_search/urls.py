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

    url(r'^semantic-search/advanced/', advance_search_view, name='advanceSearch'),

    url(r'^semantic-search/concept/', class_search_view, name='classSearch'),
    url(r'^semantic-search/get_concept/', class_search_view, name='classSearch'),

    url(r'^semantic-search/annotation/', annotation_search_view, name='annotationSearch'),
    url(r'^semantic-search/results/', annotation_search_view_results, name='annotationSearch'),

    url(r'^semantic-search/', automatic_search_view, name='automaticSearch'),

    #url(r'^semantic-search/results/', results_search_view, name='resultsQueryView'),

    ##url services##

    url(r'^semantic-search/complex/latest/', get_latest_query, name='getLatestQuery'),

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

    url(r'^class_search/', class_search_service,
        name='annotation_search_service'),

    url(r'^annotation_search/', annotation_search_service,
        name='annotation_search_service'),

    url(r'^dataset_query/', dataset_query_service,
        name='dataset_query'),

    url(r'^semantic-search/$', search_permalink, name="searchPermalink")
)
