# pyre-strict
from django.urls import path
from . import views

from typing import List, Union
from django.urls import URLResolver, URLPattern

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path('', views.resource, name='resources'),
    path('found_useful/<int:res_id>/', views.resource_found_useful, name='resource_useful'),

    path('resource_search/', views.resource_search, name='resource_search'),
    path('<str:tag>', views.resource_tag, name='resources_tag'),
    path('<slug>/', views.resource_item, name='resource_item'),

]
