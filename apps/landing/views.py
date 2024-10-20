from typing import Union

from area.models import Area, PostCode
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from map.markers import river_marker
from remix.models import RemixIdea
from river.models import River


def landing(request: HttpRequest) -> Union[HttpResponseRedirect, HttpResponse]:
    if PostCode.objects.all().count() == 0 and not request.user.is_authenticated:
        return render(
            request,
            "landing/landing.html",
            {
                "show_wizard": True,
            },
        )

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("dashboard"))
    else:
        rivers = River.objects.exclude(location=None)
        markers = []
        for river in rivers:
            marker = river_marker(river)
            if marker:
                markers.append(marker)

        for idea in RemixIdea.objects.exclude(location=None):
            marker = idea.marker
            if marker:
                markers.append(marker)

        context = {"markers": markers}

        # Adding the first available area to the map. If the user is not logged in and
        # an area with a valid location exists, setting the 'home' context with its coordinates.
        # this is detected by Alpine directive in map.ts
        area = Area.objects.exclude(location=None).first()
        if area:
            context["home"] = {
                "center": area.location.coords,
                "zoom": area.zoom,
            }

        return render(request, "landing/landing.html", context)


def privacy(request: HttpRequest) -> HttpResponse:
    return render(request, "landing/privacy.html")


def handle_404(request: HttpRequest, exception: Exception = None) -> HttpResponse:
    return render(request, "404.html", status=404)


def handle_500(request: HttpRequest) -> HttpResponse:
    return render(request, "500.html", status=500)
