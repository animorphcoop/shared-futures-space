import json
import random
from typing import Any, Dict, List, Union

from django.template.loader import render_to_string

from area.models import Area
from core.utils.tags_declusterer import tag_cluster_to_list
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from river.models import River, RiverMembership


class AreaDetailView(DetailView):
    model = Area

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


class SpringView(AreaDetailView):
    template_name = "spring/spring_area.html"

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


random_coordinates = [
    [-5.9273, 54.5993],
    [-5.9236, 54.6009],
    [-5.9146, 54.6033],
    [-5.9202, 54.5967],
]


def river_marker(river: River) -> dict:
    return {
        "slug": river.slug,
        "name": river.title,
        "icon": random.sample(["pin", "circle"], 1)[0],
        "coordinates": random.sample(random_coordinates, 1)[0],
        "html": render_to_string("river/river_card.html", {"river": river}),
    }


class SpringMapView(AreaDetailView):
    template_name = "spring/spring_map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rivers = River.objects.filter(area=self.object)
        context["rivers"] = rivers
        context["markers"] = [river_marker(river) for river in rivers]
        return context


class EstuaryView(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, "spring/spring_estuary.html")
