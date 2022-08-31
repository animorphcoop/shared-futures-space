# pyre-strict
from django.http.request import HttpRequest
from django.http import HttpResponse

from .models import Resource, HowTo, CaseStudy
from django.shortcuts import render, get_object_or_404
from apps.core.utils.tags_declusterer import objects_tags_cluster_list_overwrite, single_object_tags_cluster_overwrite
from itertools import chain

from django.db.models import Q

from typing import List, Optional

def resource(request: HttpRequest) -> HttpResponse:
    how_tos = objects_tags_cluster_list_overwrite(HowTo.objects.all())
    case_studies = objects_tags_cluster_list_overwrite(CaseStudy.objects.all())
    resources = list(chain(how_tos, case_studies))
    context = {'resources': resources}
    return render(request, 'resources/resources.html', context)


def resource_search(request: HttpRequest) -> HttpResponse:
    search_text = request.POST.get('search')

    results = filter_and_cluster_resources(search_text)
    context = {'results': results}
    return render(request, 'resources/partials/search_results.html', context)


def resource_tag(request: HttpRequest, tag) -> HttpResponse:
    #search_text = request.POST.get('search')


    how_tos = objects_tags_cluster_list_overwrite(HowTo.objects.all())
    case_studies = objects_tags_cluster_list_overwrite(CaseStudy.objects.all())
    resources = list(chain(how_tos, case_studies))
    context = {'resources': resources,
               'tag': tag}
    return render(request, 'resources/resources.html', context)


def filter_and_cluster_resources(search_term: Optional[str]) -> List:  # pyre-ignore[24]
    how_tos = HowTo.objects.filter(Q(title__icontains=search_term)
                                   | Q(summary__icontains=search_term)
                                   | Q(tags__name__icontains=search_term)).distinct()

    case_studies = CaseStudy.objects.filter(Q(title__icontains=search_term)
                                            | Q(summary__icontains=search_term)
                                            | Q(tags__name__icontains=search_term)).distinct()
    # can iterate over tags only after filtering
    how_tos = objects_tags_cluster_list_overwrite(how_tos)
    case_studies = objects_tags_cluster_list_overwrite(case_studies)
    return list(chain(how_tos, case_studies))


def resource_item(request: HttpRequest, slug: Optional[str]) -> HttpResponse:
    current_resource = None
    try:
        current_resource = HowTo.objects.get(slug=slug)
    except HowTo.DoesNotExist:
        try:
            current_resource = CaseStudy.objects.get(slug=slug)
        except CaseStudy.DoesNotExist:
            print('it is neither HowTo nor CaseStudy')
    context = {
        'resource': single_object_tags_cluster_overwrite(current_resource)
    }

    return render(request, 'resources/resource_item.html', context)
