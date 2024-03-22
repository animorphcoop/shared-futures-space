from django.template.loader import render_to_string
from resources.models import CaseStudy, HowTo
from river.models import River
from typing_extensions import Optional


def river_marker(river: River) -> Optional[dict]:
    if not river.location:
        return None
    return {
        "type": "river",
        "slug": river.slug,
        "name": river.title,
        "icon": "pin",
        "coordinates": river.location.coords,
        "approximate": not river.location_exact,
        "html": render_to_string(
            "river/river_card.html",
            {"river": river, "close_button": True, "view_button": True},
        ),
        "htmlMini": render_to_string("river/river_card_mini.html", {"river": river}),
    }


def case_study_marker(case_study: CaseStudy) -> Optional[dict]:
    if not case_study.location:
        return None
    return {
        "type": "resource",
        "slug": case_study.slug,
        "name": case_study.title,
        "coordinates": case_study.location.coords,
        "approximate": not case_study.location_exact,
        "html": render_to_string(
            "resources/partials/resources-card.html",
            {"resource": case_study, "close_button": True, "view_button": True},
        ),
    }


def how_to_marker(how_to: HowTo) -> Optional[dict]:
    if not how_to.location:
        return None
    return {
        "type": "resource",
        "slug": how_to.slug,
        "name": how_to.title,
        "coordinates": how_to.location.coords,
        "html": render_to_string(
            "resources/partials/resources-card.html",
            {"resource": how_to, "close_button": True, "view_button": True},
        ),
        "htmlMini": "<h2>" + how_to.title + "</h2>",
    }
