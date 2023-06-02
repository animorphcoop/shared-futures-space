from django.urls import path
from . import views

from typing import List, Union
from django.urls import URLResolver, URLPattern

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path('check_url_nav/', views.check_url_nav, name='check_url_nav'),

]
