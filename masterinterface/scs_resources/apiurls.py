__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'

from django.conf.urls import patterns, url
from piston.resource import Resource
from masterinterface.scs_resources.api import has_local_roles, get_resources_list


has_local_roles_entries = Resource(handler=has_local_roles)
get_resources_list_entries = Resource(handler=get_resources_list)

urlpatterns = patterns(
    url(r'^hasrole', has_local_roles_entries),
    url(r'^hasrole/', has_local_roles_entries),
    url(r'^hasrole\.(?P<emitter_format>.+)', has_local_roles_entries),
    url(r'^resources', get_resources_list_entries),
    url(r'^resources/', get_resources_list_entries),
    url(r'^resources\.(?P<emitter_format>.+)', get_resources_list_entries),

)
