from typing import Union

from area.models import PostCode
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from map.markers import river_marker
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
        context = {"markers": markers}
        return render(request, "landing/landing.html", context)


def privacy(request: HttpRequest) -> HttpResponse:
    return render(request, "landing/privacy.html")


def handle_404(request: HttpRequest, exception: Exception = None) -> HttpResponse:
    return render(request, "404.html", status=404)


def handle_500(request: HttpRequest) -> HttpResponse:
    print("500 error handled with redirect")
    return HttpResponseRedirect(reverse("resources"))
