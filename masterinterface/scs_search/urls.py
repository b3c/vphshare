__author__ = ""

from django.conf.urls import patterns, url, include
from views import *

urlpatterns = patterns(

    'scs_search.views',
    url(r'^search/$', automaticSearchView , name='automaticSearchView'),

    )