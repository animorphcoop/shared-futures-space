from django.views.generic import TemplateView

from remix.markers import river_marker, case_study_marker
from resources.models import CaseStudy, HowTo
from river.models import River


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

        for case_study in CaseStudy.objects.exclude(location=None):
            marker = case_study_marker(case_study)
            if marker:
                markers.append(marker)

        for how_to in HowTo.objects.exclude(location=None):
            marker = case_study_marker(how_to)
            if marker:
                markers.append(marker)

        context["markers"] = markers
        return context
