from django.conf.urls import patterns, url

from views import *

urlpatterns = patterns(
    'scs_resources.views',
    url(r'^resources/request_for_sharing/$', request_for_sharing),
    url(r'^resources/form/addLink/$', add_link_to_form),
    url(r'^resources/form/addFile/$', add_file_to_form),
    url(r'^resources/search_as/$', smart_get_AS, name='smart_get_AS'),
    url(r'^resources/search_sws/$', smart_get_SWS, name='smart_get_SWS'),
    url(r'^resources/search/$', smart_get_resources, name='smart_get_resources'),
    url(r'^resources/edit/(?P<id>[\w\-]+)/$', edit_resource, name='editResource'),
    url(r'^resources/(?P<id>[\w\-]+)/$', resource_detailed_view),
    url(r'^dashboard/$', manage_resources,  name='manage-data'),
    url(r'^dashboard/newshare$', newshare,  name='newshare'),
    url(r'^dashboard/rejectRequest$', rejectRequest,  name='rejectRequest'),
    url(r'^dashboard/acceptRequest$', acceptRequest,  name='acceptRequest'),
    url(r'^grantrole/$', grant_role),
    url(r'^revokerole/$', revoke_role),
    url(r'^createrole/$', create_role),
    url(r'^workflows/$', workflowsView, name='workflows'),
    url(r'^workflows/search-workflow/$', search_workflow ,  name='search-workflow'),
    url(r'^workflows/new/$', create_workflow, name='createWorkflows'),
    url(r'^workflows/edit/(?P<id>\d+)/$', edit_workflow, name='editWorkflow'),

)

