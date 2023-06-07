from random import shuffle
from typing import List

from django import template

from ..models import CaseStudy

register = template.Library()


@register.simple_tag
def get_case_studies() -> List[str]:
    case_studies = []
    for case_study in CaseStudy.objects.all():
        if case_study.case_study_image is not None:
            case_studies.append(case_study)
    shuffle(case_studies)
    return case_studies[:3]
