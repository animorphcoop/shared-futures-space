# pyre-strict
from django import template
from ..models import CaseStudy

from typing import List
from random import shuffle

register = template.Library()

@register.simple_tag
def get_case_studies() -> List[str]:
    case_studies = []
    for case_study in CaseStudy.objects.all():
            case_studies.append(case_study)
    shuffle(case_studies)
    return case_studies[:3]
