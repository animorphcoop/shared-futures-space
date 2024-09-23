from typing import List, Union

from django.contrib.auth.decorators import login_required
from django.urls import URLPattern, URLResolver, path

from .views import (
    CreateRemixView,
    RemixIdeaChatMessageListView,
    RemixIdeaChatUpdateView,
    RemixIdeaChatView,
    RemixIdeaStartWizardView,
    RemixIdeaView,
    RemixMapView,
    RemixView,
    UpdateRemixView,
)

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path(
        "map/",
        RemixMapView.as_view(),
        name="remix_map",
    ),
    path(
        "create/idea/",
        login_required(RemixIdeaStartWizardView.as_view()),
        name="start_remix_idea",
    ),
    path(
        "idea/<uuid:uuid>/",
        RemixIdeaView.as_view(),
        name="remix_idea",
    ),
    path(
        "idea/<uuid:uuid>/chat/",
        RemixIdeaChatView.as_view(),
        name="remix_idea_chat",
    ),
    path(
        "idea/<uuid:uuid>/chat/count/",
        RemixIdeaChatUpdateView.as_view(),
        name="remix_idea_chat_message_count",
    ),
    path(
        "idea/<uuid:uuid>/chat/message_list/",
        RemixIdeaChatMessageListView.as_view(
            template_name="messaging/message_list.html"
        ),
        name="remix_idea_chat_message_list",
    ),
    path(
        "create/remix/", login_required(CreateRemixView.as_view()), name="create_remix"
    ),
    path(
        "<uuid:uuid>/",
        login_required(RemixView.as_view()),
        name="remix",
    ),
    path(
        "<int:pk>/update/",
        login_required(UpdateRemixView.as_view()),
        name="remix_update",
    ),
]
