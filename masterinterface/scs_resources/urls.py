from django.conf.urls import patterns, url

from views import *

urlpatterns = patterns(
    'scs_resources.views',
    url(r'^datashare/$', resource_share_widget),
    url(r'^resources/request_for_sharing/$', request_for_sharing),
    url(r'^resources/(?P<id>[\w\-]+)/$', resource_detailed_view),
    url(r'^data/manage-data/$', manage_resources,  name='manage-data'),
    url(r'^grantrole/$', grant_role),
    url(r'^revokerole/$', revoke_role),
    url(r'^createrole/$', create_role),
    url(r'^workflows/$', workflowsView, name='workflows'),
    url(r'^workflows/search-workflow/$', search_workflow ,  name='search-workflow'),
    url(r'^workflows/new/$', create_workflow, name='createWorkflows'),
    url(r'^workflows/edit/(?P<id>\d+)/$', edit_workflow, name='editWorkflow'),
)

