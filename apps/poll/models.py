# pyre-strict

from django.core.exceptions import ValidationError
from django.db import models
from uuid import uuid4

from userauth.models import CustomUser # pyre-ignore[21]

from typing import List

def validate_poll_options(value: List[str]) -> bool:
    if type(value) == list and all(map(lambda x: type(x) == str, value)):
        return True
    else:
        raise ValidationError('poll options must be a list of strings (got ' + repr(value) + ')')

class Poll(models.Model):
    uuid: models.UUIDField = models.UUIDField(default = uuid4)
    question: models.CharField = models.CharField(max_length = 100)
    options: models.JSONField = models.JSONField(validators = [validate_poll_options])

class Vote(models.Model):
    user: models.ForeignKey = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    poll: models.ForeignKey = models.ForeignKey(Poll, on_delete = models.CASCADE)
    choice: models.IntegerField = models.IntegerField()
    def clean(self) -> None: # pyre insists this returns None, dunno why
        cleaned_data = super().clean()
        # 0 indicates the always-present unask-the-question option
        if self.choice < 0 or self.choice > len(self.poll.options):
            raise ValidationError('not a valid choice for that poll (got ' + str(self.choice) + ', expected an integer in 0 - ' + str(len(self.poll.options)) + ')')
        else:
            return cleaned_data
