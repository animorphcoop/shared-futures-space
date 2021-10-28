# pyre-strict
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse

from wagtail.core.models import Page
from wagtail.search.models import Query

from django.http import HttpRequest, HttpResponse
from typing import List, Any


def search(request: HttpRequest) -> TemplateResponse:
    search_query: str = request.GET.get('query', '')
    page: str = request.GET.get('page', '1')

    # Search
    if search_query: # the empty string is falsy
        search_results = Page.objects.live().search(search_query)
        query = Query.get(search_query)

        # Record hit
        query.add_hit()
    else:
        search_results = Page.objects.none()

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results_page = paginator.page(page)
    except PageNotAnInteger:
        search_results_page = paginator.page(1)
    except EmptyPage:
        search_results_page = paginator.page(paginator.num_pages)

    return TemplateResponse(request, 'search/search.html', {
        'search_query': search_query,
        'search_results': search_results_page,
    })
