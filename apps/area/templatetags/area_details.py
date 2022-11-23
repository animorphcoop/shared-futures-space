# pyre-strict
from django import template
from ..models import Area

from typing import OrderedDict as OD
from django.utils.text import slugify
from collections import OrderedDict

register = template.Library()

# get areas, exclude 'other' from the list and sort alphabetically
@register.simple_tag
def get_areas() -> OD[str, str]:
    areas = []
    areas_dict = OrderedDict()  # to remember order of inserting
    for area in Area.objects.all():
        if area.name != 'Other':
            areas.append(area.name)
    # sort alphabetically
    areas.sort()
    for area_name in areas:
        areas_dict[slugify(area_name)] = area_name
    return areas_dict

