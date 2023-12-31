from typing import Any, Dict, List, Union

from area.models import Area
from core.utils.tags_declusterer import tag_cluster_to_list
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import TemplateView
from river.models import River, RiverMembership

# from river.util import get_current_stage_string, get_started_months_ago


class SpringView(TemplateView):
    def get(
        self, request: HttpRequest, *args: List[Any], **kwargs: Dict[str, str]
    ) -> Union[HttpResponse, HttpResponseRedirect]:
        # RETURN URL PATH
        slug = str(kwargs["slug"])
        print(slug)
        if "-" in slug:
            name = slug.replace("-", " ")
        elif slug == "derrylondonderry":
            name = "derry~londonderry"
        else:
            name = slug

        if Area.objects.filter(name__iexact=name).exists():
            area = Area.objects.get(name__iexact=name)
        else:
            return HttpResponseRedirect(reverse("404"))

        rivers = River.objects.filter(area=area)
        for river in rivers:
            river.tags = tag_cluster_to_list(river.tags)

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

        context = {"area": area, "rivers": rivers, "num_swimmers": num_swimmers}

        return render(request, "spring/spring_area.html", context)


class EstuaryView(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, "spring/spring_estuary.html")
