from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    'cyfronet.views',
    url(r'^lobcder(.*)$', 'lobcder'),
    url(r'^filestore(.*)$', 'lobcder'),
    url(r'^tools/$', 'tools'),
    url(r'^retrivevtk/$', 'retriveVtk'),
)
