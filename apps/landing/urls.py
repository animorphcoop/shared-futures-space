from typing import List, Union

from django.urls import URLPattern, URLResolver, path

from . import views

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path("", views.landing, name="landing"),
    path("privacy/", views.privacy, name="privacy"),
    path("404/", views.handle_404, name="404"),
    path("500/", views.handle_500, name="500"),
]
