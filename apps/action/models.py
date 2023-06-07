from uuid import uuid4

from django.db import models
from river.models import River


class Action(models.Model):
    uuid: models.UUIDField = models.UUIDField(default=uuid4)
    creator: models.ForeignKey = models.ForeignKey(
        "userauth.CustomUser", on_delete=models.CASCADE, related_name="creator"
    )
    receiver: models.ForeignKey = models.ForeignKey(
        "userauth.CustomUser",
        null=True,
        on_delete=models.CASCADE,
        related_name="receiver",
    )  # null signifies that any superuser can accept it, for the request system
    kind: models.CharField = models.CharField(
        max_length=200
    )  # TODO: this should have constraints on what it can be. can't really do without some refactoring because views refers to action.kind.startswith
    result: models.CharField = models.CharField(
        max_length=10, null=True
    )  # once set, describes what happened - 'invoked', 'rejected' or 'rescinded'

    # the following entries are optional parameters that some kinds of action need
    param_river: models.ForeignKey = models.ForeignKey(
        "river.River", null=True, on_delete=models.CASCADE
    )
    param_str: models.CharField = models.CharField(max_length=2000, null=True)
