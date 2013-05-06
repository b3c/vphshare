from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    'cyfronet.views',
    url(r'^cloudmanager/$', 'cloudmanager'),
    url(r'^datamanager/$', 'datamanager'),
    url(r'^policymanager/$', 'policymanager'),

    url(r'^lobcder/create(.*)$', 'lobcderCreateDirectory'),
    url(r'^lobcder/metadata(.*)$', 'lobcderMetadata'),
    url(r'^lobcder/delete(.*)$', 'lobcderDelete'),
    url(r'^lobcder(.*)$', 'lobcder'),

    # default rollback to cloudmanager
    url(r'', 'index'),
)
