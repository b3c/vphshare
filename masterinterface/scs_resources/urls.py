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
    url(r'^resources/list/(?P<resource_type>[\w\-]+)/(?P<page>\d+)', get_resources_list),
    url(r'^resources/list/(?P<resource_type>[\w\-]+)/', get_resources_list,  name='get_resources_list'),
    url(r'^resources/(?P<global_id>[\w\-]+)/rate/(?P<rate>\d+)/', rate_resource, name='rate_resource'),
    url(r'^resources/(?P<id>[\w\-]+)/$', resource_detailed_view),
    url(r'^browse/(?P<tab>[\w\-]+)/$', resources,  name='resources_tab'),
    url(r'^browse/$', resources,  name='resources_tab'),
    url(r'^resources/$', resources, name='resources'),
    url(r'^dashboard/$', manage_resources,  name='manage-data'),
    url(r'^dashboard/newshare$', newshare,  name='newshare'),
    url(r'^dashboard/newshare/$', newshare,  name='newshare'),
    url(r'^dashboard/rejectRequest$', rejectRequest,  name='rejectRequest'),
    url(r'^dashboard/rejectRequest/$', rejectRequest,  name='rejectRequest'),
    url(r'^dashboard/acceptRequest$', acceptRequest,  name='acceptRequest'),
    url(r'^dashboard/acceptRequest/$', acceptRequest,  name='acceptRequest'),
    url(r'^dashboard/details/(?P<global_id>[\w\-]+)', get_resources_details,  name='resoruce_dashboard_detail'),
    url(r'^dashboard/share/(?P<global_id>[\w\-]+)', get_resources_share,  name='resoruce_dashboard_share'),
    url(r'^dashboard/publish/(?P<global_id>[\w\-]+)', publish_resource,  name='publish_resource'),
    url(r'^dashboard/unpublish/(?P<global_id>[\w\-]+)', unpublish_resource,  name='unpublish_resource'),
    url(r'^dashboard/markpublic/(?P<global_id>[\w\-]+)', mark_resource_public,  name='mark_resource_public'),
    url(r'^dashboard/markprivate/(?P<global_id>[\w\-]+)', mark_resource_private,  name='mark_resource_private'),
    url(r'^dashboard/list/(?P<resource_type>[\w\-]+)/(?P<page>\d+)', get_resources_list_by_author),
    url(r'^dashboard/list/(?P<resource_type>[\w\-]+)', get_resources_list_by_author,  name='resoruces_by_author'),
    url(r'^dashboard/(?P<tab>[\w\-]+)', manage_resources,  name='resoruces_by_author'),
    url(r'^grantrole/$', grant_role),
    url(r'^grantrolerecursive/$', grant_recursive_role),
    url(r'^revokerole/$', revoke_role),
    url(r'^createrole/$', create_role),
    url(r'^workflows/$', workflowsView, name='workflows'),
    url(r'^workflows/new/$', edit_resource, name='create_workflow'),
    url(r'^workflows/edit/(?P<id>\d+)/$', edit_resource, name='edit_workflow'),
    url(r'^discoveries/$', discoveries,  name='discoveries'),
    url(r'^discoveries/list/(?P<resource_type>[\w\-]+)/(?P<page>\d+)', get_discoveries_list),
    url(r'^discoveries/list/(?P<resource_type>[\w\-]+)/', get_discoveries_list,  name='get_discoveries_list'),
    url(r'^discovery/$', discovery,  name='discovery'),
    url(r'^discovery/list/(?P<resource_type>[\w\-]+)/(?P<page>\d+)', get_discovery_list),
    url(r'^discovery/list/(?P<resource_type>[\w\-]+)/', get_discovery_list,  name='get_discovery_list'),
)

