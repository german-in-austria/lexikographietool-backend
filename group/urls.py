from django.urls import path, include
from .views import *

app_name = "group"
urlpatterns = [
   
    path('group/settings/<groupId>/', get_update_group_settings, name='settings'),

    path('group/', create_group, name='group'),
    path('groups/', get_own_groups, name='get_own_groups'),
    path('groups_deleted/', get_own_groups_deleted),
    path('group_restore/<groupId>/', restore_group),
    path('groups/public/', GroupView.as_view(), name='get_public_groups'),
    path('group/<int:groupId>/<username>/', add_or_remove_user, name='addOrRemoveUser'),
    path('group/<int:groupId>/', get_update_group, name='getGroupById'),
    path('group/leave/<int:groupId>/', leave_group, name='leaveGroup'),

    path('invite/<int:groupId>/', get_invite_link, name='getInviteLink'),
    path('join/<int:groupId>/', join_group, name='joinGroup'),
    path('groupname/<int:groupId>/', get_group_name_by_id, name='getNameByInvite'), 
]