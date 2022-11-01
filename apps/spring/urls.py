# pyre-strict

from django.urls import path, URLResolver, URLPattern
from .views import SpringView

from typing import List, Union

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path('<str:slug>/', SpringView.as_view(template_name='all_rivers.html'), name='spring'),
]
