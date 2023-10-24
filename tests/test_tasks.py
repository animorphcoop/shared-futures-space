import datetime

import pytest
from django.urls import reverse
from river.models import RiverMembership
from task.models import Task

htmx_params = {
    "follow": True,
    "HTTP_HX-Request": "true",
}


@pytest.fixture(autouse=True)
def add_users_to_river(test_user, other_test_user, test_river):
    # Add test_user as river starter
    RiverMembership.objects.create(
        user=test_user,
        river=test_river,
        starter=True,
    )
    # And other_test_user as normal member
    RiverMembership.objects.create(
        user=other_test_user,
        river=test_river,
        starter=False,
    )


def test_create_task(client, test_user, test_river):
    client.force_login(test_user)
    task_add_url = reverse("river_task_add", args=[test_river.slug, "act", "general"])
    task_name = f"Do Something {datetime.datetime.now()}"
    response = client.post(
        task_add_url,
        {
            "name": task_name,
            "responsible": test_user.id,
        },
        **htmx_params,
    )
    assert response.status_code == 200
    assert task_name in response.content.decode("utf8")
    assert Task.objects.filter(name=task_name).exists()


def test_view_task_list(
    client, test_user, other_test_user, test_river, create_test_task
):
    client.force_login(test_user)
    stage_name = "act"
    topic = "general"
    task_count = 8
    for n in range(task_count):
        create_test_task(
            stage_name=stage_name,
            topic=topic,
            name=f"Example Task {n}",
            # Use multiple users to show we can view all tasks
            responsible=other_test_user if n > 4 else test_user,
        )
    task_list_url = reverse(
        "river_task_list",
        args=[test_river.slug, stage_name, topic],
    )
    response = client.get(task_list_url, **htmx_params)
    assert response.status_code == 200
    content = response.content.decode("utf8")
    for n in range(task_count):
        assert f"Example Task {n}" in content


def test_edit_task(client, test_user, test_river, other_test_user, create_test_task):
    client.force_login(test_user)
    task = create_test_task()
    assert task.responsible.id == test_user.id
    task_edit_url = reverse(
        "river_task_edit",
        args=[test_river.slug, task.stage_name, task.topic, task.uuid],
    )
    response = client.post(
        task_edit_url,
        {
            "name": task.name,
            "responsible": other_test_user.id,
        },
        **htmx_params,
    )
    assert response.status_code == 200
    task.refresh_from_db()
    assert task.responsible.id == other_test_user.id


def test_mark_task_done(client, test_user, test_river, create_test_task):
    client.force_login(test_user)
    task = create_test_task()
    assert not task.done
    task_edit_done_url = reverse(
        "river_task_edit_done",
        args=[test_river.slug, task.stage_name, task.topic, task.uuid],
    )
    response = client.post(task_edit_done_url, {"done": True}, **htmx_params)
    assert response.status_code == 200
    task.refresh_from_db()
    assert task.done


def test_cannot_mark_others_tasks_done(
    client, test_user, other_test_user, test_river, create_test_task
):
    client.force_login(other_test_user)
    task = create_test_task(responsible=test_user)
    task_edit_done_url = reverse(
        "river_task_edit_done",
        args=[test_river.slug, task.stage_name, task.topic, task.uuid],
    )
    response = client.post(task_edit_done_url, {"done": True}, **htmx_params)
    assert response.status_code == 404
