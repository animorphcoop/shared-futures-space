from typing import List, Union

from django.urls import URLPattern, URLResolver, path

from . import views

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path("check_url_nav/", views.check_url_nav, name="check_url_nav"),
]
