from django.conf.urls import patterns, url
from django.contrib import admin
from masterinterface.datasets.views import *

admin.autodiscover()

urlpatterns = patterns(
    'scs.views',
    url(r'^query_builder/(?P<global_id>[\w\-]+)/$', query_builder, name='query_builder'),
    url(r'^get_dataset_schema/$', get_dataset_schema, name='get_dataset_schema'),
)

