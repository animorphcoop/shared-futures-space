# pyre-strict
from django.urls import path
from . import views

from typing import List, Union
from django.urls import URLResolver, URLPattern

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path('', views.all_tags, name='alltags'),
    path('<str:tag_name>', views.tag, name='tag')
]
