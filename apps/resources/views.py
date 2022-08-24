# pyre-strict
from django.http.request import HttpRequest
from django.http import HttpResponse

from .models import Resource, HowTo, CaseStudy
from django.shortcuts import render
from apps.core.helpers.tags_declusterer import objects_tags_cluster_list_overwrite
from itertools import chain

from django.db.models import Q
import operator
import functools

def resource(request: HttpRequest) -> HttpResponse:
    how_tos = objects_tags_cluster_list_overwrite(HowTo.objects.all())
    case_studies = objects_tags_cluster_list_overwrite(CaseStudy.objects.all())
    resources = list(chain(how_tos, case_studies))
    context = {'resources': resources}
    return render(request, 'resources/resources.html', context)

#TODO: search-results template to be merged with list template as they duplicate styles (or export styles)
def resource_search(request: HttpRequest) -> HttpResponse:
    search_text = request.POST.get('search')
    how_tos = objects_tags_cluster_list_overwrite(HowTo.objects.all())
    case_studies = objects_tags_cluster_list_overwrite(CaseStudy.objects.all())


    results = list(chain(
        how_tos.filter(Q(title__icontains=search_text)
                       | Q(summary__icontains=search_text)
                       | Q(tags__name__icontains=search_text)
                       ),

        case_studies.filter(Q(title__icontains=search_text)
                       | Q(summary__icontains=search_text)
                       | Q(tags__name__icontains=search_text)
                       ),
    ))

    context = {'results': results}
    return render(request, 'resources/partials/search-results.html', context)


