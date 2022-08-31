#import pytest
from django.urls import reverse

from resources.models import HowTo, CaseStudy

'''
@pytest.mark.django_db
def test_resource_add():
    how_to_res = HowTo.objects.create(title='howtitle', summary='not much to say, do it yourself',
                                      link='https://animorph.coop/')
    how_to_res.tags.add("newtag", "oldtag")
    print(how_to_res.tags.all())
    case_study_res = CaseStudy.objects.create(title='case study title', summary='not much to say, do it yourself',
                                              link='https://animorph.coop/')
    case_study_res.tags.add("casetag", "studytag")
    print(case_study_res.tags.all())
'''

def test_resource_view(client, test_resources):
    resources_page = client.get(reverse('resources'))
    assert resources_page
    print('resource view')


def test_resource_search():
    print('resource search')


#slug needed
def test_resource_item(client, test_resource):
    #resource_page = client.get(reverse('resource_item'))
    #assert resource_page
    print('resource item')
