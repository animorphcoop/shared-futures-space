# pyre-strict
from django.urls import path
from . import views

from typing import List, Union
from django.urls import URLResolver, URLPattern

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path('', views.resource, name='resources'),
    path('search=<str:tag>', views.resource_tag, name='resources_tag'),
    path('<slug>/', views.resource_item, name='resource_item'),

]
