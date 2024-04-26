from typing import List, Union

from django.urls import URLPattern, URLResolver, path

from .views import RemixView

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path(
        "",
        RemixView.as_view(),
        name="remix",
    ),
]
