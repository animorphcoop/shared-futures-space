from typing import List, Union

from django.contrib.auth.decorators import login_required
from django.urls import URLPattern, URLResolver, path

from .views import (
    RemixPlaygroundView,
    RemixIdeaView,
    RemixIdeaStartWizardView,
    RemixMapView,
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
        "create/",
        RemixIdeaStartWizardView.as_view(),
        name="start_remix_idea",
    ),
    path(
        "<uuid:uuid>/",
        RemixIdeaView.as_view(),
        name="remix_idea_view",
    ),
]
