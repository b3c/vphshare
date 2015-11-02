from django.conf.urls import patterns, url
from django.contrib import admin
from masterinterface.cilab_ejobs.views import ejobs_view_get

admin.autodiscover()

urlpatterns = patterns(
    'scs.views',
    url(r'^ejobs/$', ejobs_view_get, name='ejobs_view_get'),
)

