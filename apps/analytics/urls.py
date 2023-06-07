from typing import List, Union

from django.urls import URLPattern, URLResolver, path

from .views import AnalyticsView

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path(
        "",
        AnalyticsView.as_view(template_name="analytics/analytics.html"),
        name="analytics",
    )
]
