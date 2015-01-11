from django.conf.urls import patterns, url
from django.contrib import admin
from masterinterface.datasets.views import *

admin.autodiscover()

urlpatterns = patterns(
    'scs.views',
    url(r'^query_builder/(?P<global_id>[\w\-]+)/$', query_builder, name='query_builder'),
    url(r'^get_dataset_schema/$', get_dataset_schema, name='get_dataset_schema'),
    url(r'^get_results/$', get_results, name='get_results'),
    url(r'^save_the_query/$', save_the_query, name='save_the_query'),
    url(r'^edit_the_query/$', edit_the_query, name='edit_the_query'),
    url(r'^delete_the_query/$', delete_the_query, name='edit_the_query'),
)

