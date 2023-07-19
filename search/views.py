from typing import Any, List

from django.core.paginator import EmptyPage
from django.core.paginator import Page as PaginatorPage
from django.core.paginator import PageNotAnInteger, Paginator
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from wagtail.models import Page
from wagtail.search.models import Query


def search(request: HttpRequest) -> TemplateResponse:
    search_query: str = request.GET.get("query", "")
    page: str = request.GET.get("page", "1")
    search_results_page: PaginatorPage = Page.objects.none()

    # Search
    if search_query:  # the empty string is falsy
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

    return TemplateResponse(
        request,
        "search/search.html",
        {
            "search_query": search_query,
            "search_results": search_results_page,
        },
    )
