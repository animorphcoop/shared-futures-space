import pytest
from django.urls import reverse
from resources.models import HowTo, CaseStudy
from core.utils.tags_declusterer import tag_cluster_to_list
from itertools import chain
import bs4

def test_resource_add(client, test_user, test_image):
    # required for wagtail access
    test_user.is_superuser = True
    test_user.save()
    client.force_login(test_user)
    # HowTo
    client.post('/admin/resources/howto/create/', {'title': 'test howto', 'summary': 'summary of test', 'link': 'https://example.com', 'tags': 'tag1,tag2'})
    new_howto = HowTo.objects.get(title = 'test howto')
    assert new_howto.summary == 'summary of test'
    assert len(tag_cluster_to_list(new_howto.tags)) == 2
    assert 'tag1' in map(str, tag_cluster_to_list(new_howto.tags))
    # CaseStudy
    client.post('/admin/resources/casestudy/create/', {'title': 'test case study', 'summary': 'summary of test', 'link': 'https://example.com', 'case_study_image': test_image.id,
                                                       'body-count': '1', 'body-0-deleted': '', 'body-0-order': '0', 'body-0-type': 'body_text', 'body_0-id': 'da582675-1d36-4151-8fad-9c86449bada7',
                                                       'body-0-value-content': '{"blocks":[{"key":"qjt40","text":"test body text","type":"unstyled","depth":0,"inlineStyleRanges":[],"entityRanges":[],"data":{}}],"entityMap":{}}',
                                                       'tags': 'tag1,tag2'})
    new_casestudy = CaseStudy.objects.get(title = 'test case study')
    assert new_casestudy.summary == 'summary of test'
    assert len(tag_cluster_to_list(new_casestudy.tags)) == 2
    assert new_casestudy.case_study_image == test_image

    # disable supersuser, don't know if necessary
    test_user.is_superuser = False
    test_user.save()

def test_resource_search(client, test_how_to_resource, test_case_study_resource):
    resource_page = str(client.get(reverse('resources')).content)
    assert test_how_to_resource.title in resource_page
    assert test_case_study_resource.title in resource_page
    
    howto_url_search = str(client.get(reverse('resources_tag', args=[test_how_to_resource.title])).content)
    assert test_how_to_resource.summary in howto_url_search
    casestudy_url_search = str(client.get(reverse('resources_tag', args=['how'])).content)
    assert test_case_study_resource.summary in casestudy_url_search

    howto_post_search = str(client.post(reverse('resource_search'), {'search': test_how_to_resource.title}).content)
    assert test_how_to_resource.summary in howto_post_search
    casestudy_post_search = str(client.post(reverse('resource_search'), {'search': test_how_to_resource.title}).content)
    assert test_case_study_resource.summary in casestudy_post_search


def test_resource_item(client, test_how_to_resource):
    how_to = test_how_to_resource
    resource_item_page = client.post(reverse('resource_item', args=[how_to.slug]))
    resource_item_page_html = bs4.BeautifulSoup(resource_item_page.content, features='html5lib')
    assert resource_item_page_html.body.find_all('h4', string=" howtitle")

