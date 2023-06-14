from typing import List, Union

from django.urls import URLPattern, URLResolver, path

from . import views

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path("", views.dashboard, name="dashboard"),
    path("wizard/", views.wizard, name="wizard"),
    path("contact/", views.contact, name="contact"),
]
