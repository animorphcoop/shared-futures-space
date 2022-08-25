# pyre-strict
from django.http.request import HttpRequest
from django.http import HttpResponse

from .models import Resource, HowTo, CaseStudy
from django.shortcuts import render, get_object_or_404
from apps.core.helpers.tags_declusterer import objects_tags_cluster_list_overwrite
from itertools import chain

from django.db.models import Q

from django.shortcuts import get_object_or_404



def resource(request: HttpRequest) -> HttpResponse:
    how_tos = objects_tags_cluster_list_overwrite(HowTo.objects.all())
    case_studies = objects_tags_cluster_list_overwrite(CaseStudy.objects.all())
    resources = list(chain(how_tos, case_studies))
    context = {'resources': resources}
    return render(request, 'resources/resources.html', context)


def resource_search(request: HttpRequest) -> HttpResponse:
    search_text = request.POST.get('search')
    how_tos = HowTo.objects.all()
    case_studies = CaseStudy.objects.all()

    # filter through key shared fields
    how_tos.filter(Q(title__icontains=search_text)
                   | Q(summary__icontains=search_text)
                   | Q(tags__name__icontains=search_text))

    case_studies.filter(Q(title__icontains=search_text)
                        | Q(summary__icontains=search_text)
                        | Q(tags__name__icontains=search_text))

    # can iterate over tags only after filtering
    how_tos = objects_tags_cluster_list_overwrite(how_tos)
    case_studies = objects_tags_cluster_list_overwrite(case_studies)

    results = list(chain(how_tos, case_studies))

    context = {'results': results}
    return render(request, 'resources/partials/search_results.html', context)


def resource_item(request: HttpRequest, slug) -> HttpResponse:
    current_resource = None
    try:
        current_resource = HowTo.objects.get(slug=slug)
    except HowTo.DoesNotExist:
        print('it is not a howto')

    if current_resource is None:
        try:
            current_resource = CaseStudy.objects.get(slug=slug)
        except CaseStudy.DoesNotExist:
            print('it is not a case study')

    context = {
        'resource': current_resource
    }

    return render(request, 'resources/resource_item.html', context)
