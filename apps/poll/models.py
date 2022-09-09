# pyre-strict

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from uuid import uuid4

from userauth.models import CustomUser # pyre-ignore[21]

from typing import List, Dict

def validate_poll_options(value: List[str]) -> bool:
    if type(value) == list and all(map(lambda x: type(x) == str, value)):
        return True
    else:
        raise ValidationError('poll options must be a list of strings (got ' + repr(value) + ')')

class Poll(models.Model):
    uuid: models.UUIDField = models.UUIDField(default = uuid4)
    question: models.CharField = models.CharField(max_length = 100)
    options: models.JSONField = models.JSONField(validators = [validate_poll_options])
    voter_num: models.PositiveIntegerField = models.PositiveIntegerField()
    expires: models.DateTimeField = models.DateTimeField()
    closed: models.BooleanField = models.BooleanField(default = False)
    @property
    def current_results(self) -> Dict[str,List[CustomUser]]: # pyre-ignore[11]
        votes = Vote.objects.filter(poll = self)
        results = {self.options[n-1] if n != 0 else 'poll is wrong':[] for n in range(len(self.options) + 1)}
        for vote in votes:
            results[self.options[vote.choice - 1] if vote.choice != 0 else 'poll is wrong'].append(vote.user)
        return results
    def check_closed(self) -> bool:
        if self.closed:
            print('already closed')
            return True
        elif self.expires < timezone.now():
            print('timed out')
            self.closed = True
            self.save()
            return True
        else:
            vote_nums = sorted([len(Vote.objects.filter(poll = self, choice = option)) for option in range(len(self.options)+1)], reverse = True)
            if vote_nums[0] > vote_nums[1] + self.voter_num - sum(vote_nums):
                # if all remaining votes went to the current second-place option it still wouldn't equal the top option
                self.closed = True
                self.save()
                return True
            else:
                return False
            

class Vote(models.Model):
    user: models.ForeignKey = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    poll: models.ForeignKey = models.ForeignKey(Poll, on_delete = models.CASCADE)
    choice: models.IntegerField = models.IntegerField()
    def clean(self) -> None:
        cleaned_data = super().clean()
        # 0 indicates the always-present unask-the-question option
        if self.choice < 0 or self.choice > len(self.poll.options):
            raise ValidationError('not a valid choice for that poll (got ' + str(self.choice) + ', expected an integer in 0 - ' + str(len(self.poll.options)) + ')')
        else:
            return cleaned_data
