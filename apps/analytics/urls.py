from django.urls import path, URLResolver, URLPattern
from .views import AnalyticsView
from typing import List, Union

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path('', AnalyticsView.as_view(template_name = 'analytics/analytics.html'), name = 'analytics')
]
