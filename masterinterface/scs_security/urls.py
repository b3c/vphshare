
from django.conf.urls import patterns, url

from views import *

urlpatterns = patterns(
    'scs_security.views',
    url(r'^$', 'index' ),
    url(r'^policy/$', 'index', name='policy' ),
    url(r'^configuration/$', 'index', name='security_configuration'),
    url(r'^configuration/new$', 'configuration' ),
    url(r'^configuration/(?P<remote_id>[\w\-]+)/', 'configuration'),
    url(r'^configuration/(?P<remote_id>[\w\-]+)', 'configuration'),
    url(r'^configuration/(?P<remote_id>[\w\-]+)/edit/', 'configuration'),
    url(r'^configuration/(?P<remote_id>[\w\-]+)/edit', 'configuration'),
    url(r'^configuration/(?P<remote_id>[\w\-]+)/delete/', 'delete_configuration'),
    url(r'^configuration/(?P<remote_id>[\w\-]+)/delete', 'delete_configuration'),
    url(r'^policy/form/new_attribute/$', 'new_attribute' ),
    url(r'^policy/form/new_post_field/$', 'new_post_field' ),
    url(r'^policy/new$', 'new_policy' ),
    url(r'^policy/new/$', 'new_policy' ),
    url(r'^policy/(?P<remote_id>[\w\-]+)/edit', 'new_policy' ),
    url(r'^policy/(?P<remote_id>[\w\-]+)/edit/', 'new_policy' ),
    url(r'^policy/(?P<remote_id>[\w\-]+)/delete', 'delete_policy' ),
    url(r'^policy/(?P<remote_id>[\w\-]+)/delete/', 'delete_policy' ),
    url(r'^policy/(?P<remote_id>[\w\-]+)', 'new_policy'),
    url(r'^policy/(?P<remote_id>[\w\-]+)/', 'new_policy'),
)