from django.views.generic import TemplateView

from river.models import River
from river.util import river_marker


class RemixMapView(TemplateView):
    template_name = "remix/remix_map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rivers = River.objects.exclude(location=None)
        context["rivers"] = rivers
        markers = []
        for river in rivers:
            marker = river_marker(river)
            if marker:
                markers.append(marker)
        context["markers"] = markers
        return context
