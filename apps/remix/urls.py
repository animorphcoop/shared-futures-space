from typing import List, Union

from django.urls import URLPattern, URLResolver, path

from .views import RemixMapView

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path(
        "map/",
        RemixMapView.as_view(),
        name="remix_map",
    ),
]

