from typing import List, Union

from django.contrib.auth.decorators import login_required
from django.urls import URLPattern, URLResolver, path

from .views import (
    RemixView,
    RemixIdeaView,
    RemixIdeaStartWizardView,
)

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path(
        "",
        RemixView.as_view(),
        name="remix",
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
