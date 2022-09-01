import pytest
from django.urls import reverse

from resources.models import HowTo, CaseStudy


@pytest.mark.django_db
def test_resource_add():
    how_to_res = HowTo.objects.create(title='howtitle', summary='not much to say, do it yourself',
                                      link='https://animorph.coop/', tags=['how to', 'urban garden', 'leisure'])
    print(how_to_res.tags[1])
    assert how_to_res.tags[1] == 'urban garden'
    case_study_res = CaseStudy.objects.create(title='case study title', summary='not much to say, do it yourself',
                                              link='https://animorph.coop/')
    assert len(case_study_res.tags.all()) == 0
    case_study_res.tags.add('case study', 'other tag')
    # assert case_study_res.tags.all()[0] == 'case study' Taggit issue addressed in core/utils/tags_declusterer
    assert len(case_study_res.tags.all()) == 2


'''
def test_resources_view(client, test_how_to_resource):
    #resources_page = client.get(reverse('resources'))
    how_to = test_how_to_resource()
    #case_studies = CaseStudy.objects.create(test_case_study_resources)
    print("printing ", how_to)
    print(how_to.title)
    #assert how_to.title=='howtitle'


def test_resource_search():
    print('resource search')


#slug needed
def test_resource_item(client, test_how_to_resource):
    #resource_page = client.get(reverse('resource_item'))
    #assert resource_page
    print('resource item')

'''
