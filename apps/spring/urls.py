from typing import List, Union

from django.urls import URLPattern, URLResolver, path

from .views import SpringView

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path(
        "<str:slug>/",
        SpringView.as_view(template_name="spring/spring_area.html"),
        name="spring",
    ),
]
