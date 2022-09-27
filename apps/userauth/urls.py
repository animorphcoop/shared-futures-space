# pyre-strict
from django.conf import settings
from django.urls import include, path, URLResolver, URLPattern
from django.contrib.auth.decorators import login_required
from .views import CustomUserUpdateView, CustomUserDeleteView, profile_view, user_request_view, AdminRequestView, \
    CustomUserPersonalView, CustomLoginView, UserChatView, UserAllChatsView, user_detail, check_email, \
    CustomPasswordResetView
from typing import List, Union
from uuid import UUID

# !!! when adding new urls, don't forget to make them login_required if appropriate!
urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path('login/', CustomLoginView.as_view(), name='account_login'),
    path('password/reset/', CustomPasswordResetView.as_view(), name='account_password_reset'),

    path('request/', login_required(user_request_view), name='account_request'),
    path('managerequests/', login_required(AdminRequestView.as_view(template_name='account/manage_requests.html')), name='account_request_panel'),  # pyre-ignore[16]
    # path('view/', login_required(profile_view), name='account_view'),
    path('view/', profile_view, name='account_view'),

    # path('view/<int:pk>/', user_detail, name='user_detail'),
    path('add_data/', login_required(CustomUserPersonalView.as_view(template_name='account/add_data.html')),
         name='account_add_data'),
    path('delete/', login_required(CustomUserDeleteView.as_view(template_name='account/delete.html')),
         name='account_delete'),
    path('chat/', login_required(UserAllChatsView.as_view(template_name='account/all_user_chats.html')),
         name='account_all_chats'),
    path('chat/<uuid:other_uuid>/', login_required(UserChatView.as_view(template_name='account/user_chat.html')), name='user_chat'),  # pyre-ignore[16]

    # add override of signup url with custom name so we dont hardcode paths

    path('check_email/', check_email, name='check_email'),
    path('update/', login_required(CustomUserUpdateView.as_view(template_name='account/update.html')),
         name='account_update'),

    # add all paths that are not custom
    path('', include('allauth.urls')),

    # not to intercept any other paths that are not listed as custom but come from allauth
    path('<str:slug>/', user_detail, name='user_detail'),

]
