from typing import List, Union

from django.urls import URLPattern, URLResolver, path

from .views import MapView

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path(
        "",
        MapView.as_view(),
        name="map",
    ),
]
