from area.models import Area
from django.http import Http404
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from river.models import River, RiverMembership


class SpringView(DetailView):
    model = Area
    template_name = "spring/spring_area.html"

    def get_object(self):
        slug = self.kwargs.get("slug")
        if "-" in slug:
            name = slug.replace("-", " ")
        elif slug == "derrylondonderry":
            name = "derry~londonderry"
        else:
            name = slug
        try:
            return Area.objects.get(name__iexact=name)
        except Area.DoesNotExist:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        area = self.object
        rivers = River.objects.filter(area=area)
        for river in rivers:
            river.us = RiverMembership.objects.filter(river=river)
            river.swimmers = RiverMembership.objects.filter(river=river).values_list(
                "user", flat=True
            )

            river.current_stage = river.get_current_stage_string
            river.months_since = river.get_started_months_ago

            river.extra_swimmers = 0
            if len(river.swimmers) > 4:
                river.extra_swimmers = len(river.swimmers) - 4

            river.membership = RiverMembership.objects.filter(river=river)

        # This is total number for the spring
        num_swimmers = (
            RiverMembership.objects.filter(river__in=River.objects.filter(area=area))
            .values_list("user", flat=True)
            .distinct()
            .count()
        )

        context["area"] = area
        context["rivers"] = rivers
        context["num_swimmers"] = num_swimmers

        return context


class EstuaryView(TemplateView):
    template_name = "spring/spring_estuary.html"
