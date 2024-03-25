from core.utils.tags_declusterer import tag_cluster_to_list
from django.urls import reverse
from resources.models import CaseStudy, HowTo
from resources.views import filter_and_cluster_resources


def test_resource_add(client, test_user, test_image):
    # required for wagtail access
    test_user.is_superuser = True
    test_user.save()
    client.force_login(test_user)
    # HowTo
    client.post(
        "/admin/resources/howto/create/",
        {
            "title": "test howto",
            "summary": "summary of test",
            "link": "https://example.com",
            "tags": "tag1,tag2",
        },
    )
    new_howto = HowTo.objects.get(title="test howto")
    assert new_howto.summary == "summary of test"
    assert len(tag_cluster_to_list(new_howto.tags)) == 2
    assert "tag1" in map(str, tag_cluster_to_list(new_howto.tags))
    # CaseStudy
    client.post(
        "/admin/resources/casestudy/create/",
        {
            "title": "test case study",
            "summary": "summary of test",
            "link": "https://example.com",
            "case_study_image": test_image.id,
            "body-count": "1",
            "body-0-deleted": "",
            "body-0-order": "0",
            "body-0-type": "body_text",
            "body_0-id": "da582675-1d36-4151-8fad-9c86449bada7",
            "body-0-value-content": '{"blocks":[{"key":"qjt40","text":"test body text","type":"unstyled","depth":0,"inlineStyleRanges":[],"entityRanges":[],"data":{}}],"entityMap":{}}',
            "tags": "tag1,tag2",
        },
    )
    new_casestudy = CaseStudy.objects.get(title="test case study")
    assert new_casestudy.summary == "summary of test"
    assert len(tag_cluster_to_list(new_casestudy.tags)) == 2
    assert new_casestudy.case_study_image == test_image

    # disable supersuser, don't know if necessary
    test_user.is_superuser = False
    test_user.save()


def test_resource_search(client, test_how_to_resource, test_case_study_resource):
    client.get(reverse("resources")).content.decode("utf-8")
    # we can't test the search with a request because it's done client-side by htmx requesting filter_and_cluster_resources after /resources/ loads
    assert test_how_to_resource in filter_and_cluster_resources(
        test_how_to_resource.title, order_by="oldest"
    )
    assert test_case_study_resource in filter_and_cluster_resources(
        test_case_study_resource.title, order_by="oldest"
    )


def test_resource_item(client, test_how_to_resource, test_case_study_resource):
    howto_item_page = client.get(
        reverse("resource_item", args=[test_how_to_resource.slug])
    ).content.decode("utf-8")
    assert test_how_to_resource.title in howto_item_page
    casestudy_item_page = client.get(
        reverse("resource_item", args=[test_case_study_resource.slug])
    ).content.decode("utf-8")
    assert test_case_study_resource.title in casestudy_item_page
