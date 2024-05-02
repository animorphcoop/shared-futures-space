from typing import List, Union

from django.contrib.auth.decorators import login_required
from django.urls import URLPattern, URLResolver, path

from .views import (
    RemixPlaygroundView,
    RemixIdeaView,
    RemixIdeaStartWizardView,
    RemixMapView,
    CreateRemixView,
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
        "playground/",
        RemixPlaygroundView.as_view(),
        name="remix_playground",
    ),
    path(
        "create/idea/",
        RemixIdeaStartWizardView.as_view(),
        name="start_remix_idea",
    ),
    path(
        "idea/<uuid:uuid>/",
        RemixIdeaView.as_view(),
        name="remix_idea",
    ),
    path("create/remix/", CreateRemixView.as_view(), name="create_remix"),
    path(
        "<uuid:uuid>/",
        RemixView.as_view(),
        name="remix_view",
    ),
    path(
        "<int:pk>/update/",
        UpdateRemixView.as_view(),
        name="remix_update",
    ),
]
