from django.urls import path
from . import views

from typing import List

urlpatterns: List[str] = [
    path('', views.landing, name='landing'),
]
