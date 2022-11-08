# pyre-strict
from django.conf import settings
from django.urls import include, path, re_path, URLResolver, URLPattern
from django.contrib.auth.decorators import login_required
from .views import CustomUserDeleteView, profile_view, user_request_view, AdminRequestView, \
    CustomUserPersonalView, CustomSignupView, CustomLoginView, UserChatView, UserAllChatsView, check_email, \
    CustomPasswordResetView, CustomAddDataView, CustomPasswordChangeView, CustomPasswordResetFromKeyView, chat_view
from typing import List, Union
from uuid import UUID


# !!! when adding new urls, don't forget to make them login_required if appropriate!
urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path('signup/', CustomSignupView.as_view(), name='account_signup'),

    path('login/', CustomLoginView.as_view(), name='account_login'),
    path('password/change/', CustomPasswordChangeView.as_view(), name='account_password_change'),

    path('password/reset/', CustomPasswordResetView.as_view(), name='account_password_reset'),
    re_path(
        r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        CustomPasswordResetFromKeyView.as_view(),
        name="account_reset_password_from_key",
    ),
    path('request/', login_required(user_request_view), name='account_request'),
    path('managerequests/', login_required(AdminRequestView.as_view(template_name='account/manage_requests.html')), name='account_request_panel'),  # pyre-ignore[16]
    path('view/', profile_view, name='account_view'),
    path('add_data/', login_required(CustomAddDataView.as_view(template_name='account/add_data.html')),
         name='account_add_data'),
    path('delete/', login_required(CustomUserDeleteView.as_view(template_name='account/delete.html')),
         name='account_delete'),
    path('chat/', login_required(UserAllChatsView.as_view(template_name='account/all_user_chats.html')),
         name='account_all_chats'),
    path('chat_path/<str:uuid>/', chat_view, name='user_chat_path'),
    path('chat/<str:user_path>/', login_required(UserChatView.as_view(template_name='account/user_chat.html')), name='user_chat'),  # pyre-ignore[16]

    # add override of signup url with custom name so we dont hardcode paths

    # HTMX paths
    path('check_email/', check_email, name='check_email'),
    #path('update_avatar/', login_required(CustomUserPersonalView.as_view(template_name='account/update.html')), name='account_update'),
    path('update_data/', login_required(CustomUserPersonalView.as_view()), name='account_update'),
    # add all paths that are not custom
    path('', include('allauth.urls')),

    # not to intercept any other paths that are not listed as custom but come from allauth
    path('<str:slug>/',CustomUserPersonalView.as_view(), name='user_detail'),

]
