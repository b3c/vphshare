from django.conf.urls import patterns, url
from django.contrib import admin
from masterinterface.datasets.views import *

admin.autodiscover()

urlpatterns = patterns(
    'scs.views',
    url(r'^query_builder/$', query_builder, name='query_builder'),
)

