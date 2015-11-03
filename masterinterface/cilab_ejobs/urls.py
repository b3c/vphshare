from django.conf.urls import patterns, url
from django.contrib import admin
from masterinterface.cilab_ejobs.views import ejobs_view_get, ejobs_view_delete

admin.autodiscover()

urlpatterns = patterns(
    'scs.views',
    url(r'^ejobs/$', ejobs_view_get, name='ejobs_view_get'),
    url(r'^ejobs/delete/$', ejobs_view_delete, name='ejobs_view_delete'),
)

