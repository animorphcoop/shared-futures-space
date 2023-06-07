from collections import OrderedDict
from typing import OrderedDict as OD

from django import template
from django.utils.text import slugify

from ..models import Area

register = template.Library()


# get areas, exclude 'other' from the list and sort alphabetically
@register.simple_tag
def get_areas() -> OD[str, str]:
    areas_dict = OrderedDict()  # to remember order of inserting
    for area in Area.objects.all().order_by("name"):
        if area.name != "Other":
            areas_dict[slugify(area.name)] = area.name
    return areas_dict
