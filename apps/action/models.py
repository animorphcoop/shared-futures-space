# pyre-strict

from django.db import models
from project.models import Project # pyre-ignore[21]
from uuid import uuid4

class Action(models.Model):
    uuid = models.UUIDField(default=uuid4)
    creator = models.ForeignKey('userauth.CustomUser', on_delete = models.CASCADE, related_name='creator')
    receiver = models.ForeignKey('userauth.CustomUser', null = True, on_delete = models.CASCADE, related_name='receiver') # null signifies that any superuser can accept it, for the request system
    kind = models.CharField(max_length = 200) # TODO: this should have constraints on what it can be
    result = models.CharField(max_length = 10, null = True) # once set, describes what happened - 'invoked', 'rejected' or 'rescinded'

    # the following entries are optional parameters that some kinds of action need
    param_project = models.ForeignKey('project.Project', null = True, on_delete = models.CASCADE)
    param_str = models.CharField(max_length = 2000, null = True)
