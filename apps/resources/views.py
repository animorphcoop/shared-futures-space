# pyre-strict
from django.http.request import HttpRequest
from django.http import HttpResponse

from .models import HowTo, CaseStudy, SavedResource
from django.shortcuts import render
from apps.core.utils.tags_declusterer import objects_tags_cluster_list_overwrite, single_object_tags_cluster_overwrite
from itertools import chain

from analytics.models import AnalyticsEvent, log_resource_access  # pyre-ignore[21]

from django.db.models import Q
from typing import List, Optional


def resource(request: HttpRequest) -> HttpResponse:
    resources = retrieve_and_chain_resources()
    context = {'resources': resources}
    return render(request, 'resources/resources.html', context)


# with argument as a separate url and view
def resource_tag(request: HttpRequest, tag: str) -> HttpResponse:
    resources = retrieve_and_chain_resources()
    context = {'resources': resources,
               'tag': tag}
    return render(request, 'resources/resources.html', context)


def resource_search(request: HttpRequest) -> HttpResponse:
    search_text = request.POST.get('search')
    order_by = request.POST.get('order_by')
    results = filter_and_cluster_resources(search_text, order_by) if search_text != '' else retrieve_and_chain_resources()

    if request.user.is_authenticated:
        current_user = request.user
        for resource_card in results:
            try:
                saved_instance = SavedResource.objects.get(saved_resource=resource_card, saved_by=current_user)
                resource_card.saved = saved_instance
            except SavedResource.DoesNotExist:
                pass

    context = {'results': results}
    return render(request, 'resources/partials/search_results.html', context)    

def retrieve_and_chain_resources() -> List:  # pyre-ignore[24]
    how_tos = objects_tags_cluster_list_overwrite(HowTo.objects.all())
    case_studies = objects_tags_cluster_list_overwrite(CaseStudy.objects.all())
    return list(chain(how_tos, case_studies))


def filter_and_cluster_resources(search_term: Optional[str], order_by: Optional[str]) -> List:  # pyre-ignore[24]
    how_tos = HowTo.objects.filter(Q(title__icontains=search_term)
                                   | Q(summary__icontains=search_term)
                                   | Q(tags__name__icontains=search_term)).distinct()

    case_studies = CaseStudy.objects.filter(Q(title__icontains=search_term)
                                            | Q(summary__icontains=search_term)
                                            | Q(tags__name__icontains=search_term)).distinct()
    # can iterate over tags only after filtering
    how_tos = objects_tags_cluster_list_overwrite(how_tos)
    case_studies = objects_tags_cluster_list_overwrite(case_studies)
    results = list(chain(how_tos, case_studies))
    if order_by == 'latest':
        results.sort(key=lambda r: r.published_on, reverse=True)
    elif order_by == 'most saved':
        results.sort(key=lambda r: len(SavedResource.objects.filter(saved_resource=r)), reverse=True)
    elif order_by == 'most viewed':
        results.sort(
            key=lambda r: len(AnalyticsEvent.objects.filter(type=AnalyticsEvent.EventType.RESOURCE, target_resource=r)),
            reverse=True)
    return results


# single resource item
def resource_item(request: HttpRequest, slug: Optional[str]) -> HttpResponse:
    current_resource = None
    try:
        current_resource = HowTo.objects.get(slug=slug)
    except HowTo.DoesNotExist:
        try:
            current_resource = CaseStudy.objects.get(slug=slug)
        except CaseStudy.DoesNotExist:
            print('it is neither HowTo nor CaseStudy. Redirect to root url?')

    saved_instance = None

    if request.user.is_authenticated:
        current_user = request.user
        try:
            saved_instance = SavedResource.objects.get(saved_resource=current_resource, saved_by=current_user)
        except SavedResource.DoesNotExist:
            print('does not exist')

    context = {
        'resource': single_object_tags_cluster_overwrite(current_resource),
        'saved': saved_instance,
    }

    if request.user.is_authenticated:
        log_resource_access(current_resource, request.user)

    return render(request, 'resources/resource_item.html', context)


def resource_saved(request: HttpRequest, res_id: Optional[int]) -> HttpResponse:
    resource_id = res_id
    current_user = request.user
    current_resource = None

    try:
        current_resource = HowTo.objects.get(pk=res_id)
        # is_how_to = True
    except HowTo.DoesNotExist:
        try:
            current_resource = CaseStudy.objects.get(pk=res_id)
        except CaseStudy.DoesNotExist:
            return render(request, 'partials/button-hx.html')

    saved_resource = ''
    saved_instance = None
    try:
        saved_instance = SavedResource.objects.get(saved_resource=current_resource, saved_by=current_user)
        saved_instance.delete()
    except SavedResource.DoesNotExist:
        print('no saved match')
        SavedResource.objects.create(saved_resource=current_resource,
                                     saved_by=current_user)
        saved_resource = 'saved_resource'

    context = {
        'resource_id': res_id,
        'status': saved_resource
    }

    return render(request, 'partials/button-hx.html', context)
