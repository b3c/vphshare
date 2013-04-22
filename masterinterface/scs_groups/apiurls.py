__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'


from django.conf.urls import patterns, url
from piston.resource import Resource
from api import *


search_user_entries = Resource(handler=search_user)
search_group_entries = Resource(handler=search_group)
create_group_entries = Resource(handler=create_group)
delete_group_entries = Resource(handler=delete_group)
add_user_entries = Resource(handler=add_user_to_group)
remove_user_entries = Resource(handler=remove_user_from_group)
group_members_entries = Resource(handler=group_members)
user_groups_entries = Resource(handler=user_groups)
promote_user_entries = Resource(handler=promote_user)
downgrade_user_entries = Resource(handler=downgrade_user)

urlpatterns = patterns(
    url(r'^searchuser/', search_user_entries),
    url(r'^searchuser/', search_user_entries),
    url(r'^searchuser\.(?P<emitter_format>.+)', search_user_entries),
    url(r'^searchgroup/', search_group_entries),
    url(r'^searchgroup\.(?P<emitter_format>.+)', search_group_entries),
    url(r'^creategroup/', create_group_entries),
    url(r'^creategroup\.(?P<emitter_format>.+)', create_group_entries),
    url(r'^deletegroup/', delete_group_entries),
    url(r'^deletegroup\.(?P<emitter_format>.+)', delete_group_entries),
    url(r'^adduser/', add_user_entries),
    url(r'^adduser\.(?P<emitter_format>.+)', add_user_entries),
    url(r'^removeuser/', remove_user_entries),
    url(r'^removeuser\.(?P<emitter_format>.+)', remove_user_entries),
    url(r'^groupmembers/', group_members_entries),
    url(r'^groupmembers\.(?P<emitter_format>.+)', group_members_entries),
    url(r'^usergroups/', user_groups_entries),
    url(r'^usergroups\.(?P<emitter_format>.+)', user_groups_entries),
    url(r'^promoteuser/', promote_user_entries),
    url(r'^promoteuser\.(?P<emitter_format>.+)', promote_user_entries),
    url(r'^downgradeuser/', downgrade_user_entries),
    url(r'^downgradeuser\.(?P<emitter_format>.+)', downgrade_user_entries),
)