from typing import List, Union
from uuid import UUID

from django.conf import settings
from django.urls import URLPattern, URLResolver, include, path

from .views import PollCreateView, PollView, poll_edit

# !!! when adding new urls, don't forget to make them login_required if appropriate!
urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path(
        "<uuid:uuid>/",
        PollView.as_view(),
        name="poll_view",
    ),
    path(
        "create/",
        PollCreateView.as_view(),
        name="poll_create",
    ),
    path("edit/", poll_edit, name="poll_edit"),
]
