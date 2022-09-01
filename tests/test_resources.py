import pytest
from django.urls import reverse
from resources.models import HowTo, CaseStudy
from itertools import chain
import bs4

def test_resource_add(test_how_to_resource, test_case_study_resource):
    how_to_res = test_how_to_resource
    assert how_to_res.tags[1] == 'urban garden'
    case_study_res = test_case_study_resource
    assert len(case_study_res.tags.all()) == 0
    case_study_res.tags.add('case study', 'other tag')
    # assert case_study_res.tags.all()[0] == 'case study' Taggit issue addressed in core/utils/tags_declusterer
    assert len(case_study_res.tags.all()) == 2
    assert case_study_res.slug.__contains__('case-study-title')


def test_resources_view(test_how_to_resources, test_case_study_resources):
    resources = list(chain(test_how_to_resources, test_case_study_resources))
    assert len(resources) == 4
    for field in resources[1]:
        if field.slug:
            assert field.slug.__contains__('how-title2')



def test_resource_search(test_how_to_resources, test_case_study_resources):
    # when having a list or chaining we lose ability to filter like a queryset.
    search_term = 'how'
    resources = list(chain(test_how_to_resources, test_case_study_resources))
    for resource in resources:
        for field in resource:
            if field.title.__contains__(search_term):
                assert field.summary


def test_resource_item(client, test_how_to_resource):
    how_to = test_how_to_resource
    resource_item_page = client.post(reverse('resource_item', args=[how_to.slug]))
    resource_item_page_html = bs4.BeautifulSoup(resource_item_page.content, features='html5lib')
    assert resource_item_page_html.body.find_all('h4', string=" howtitle")

