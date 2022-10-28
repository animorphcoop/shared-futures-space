# pyre-strict

from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from django.db import models
from uuid import uuid4

from userauth.models import CustomUser # pyre-ignore[21]

from typing import List, Dict, Union

class BaseVote(models.Model):
    user: models.ForeignKey = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    poll: models.ForeignKey = models.ForeignKey("poll.BasePoll", on_delete = models.CASCADE)

class SingleVote(BaseVote):
    choice: models.IntegerField = models.IntegerField(null = True, default = None)
    def clean(self) -> None:
        cleaned_data = super().clean()
        # 0 indicates the always-present unask-the-question option
        if self.choice < 0 or self.choice > len(self.poll.options):
            raise ValidationError('not a valid choice for that poll (got ' + str(self.choice) + ', expected an integer in 0 - ' + str(len(self.poll.options)) + ')')
        else:
            return cleaned_data

class MultipleVote(BaseVote):
    choice: ArrayField = ArrayField(models.IntegerField())

def validate_poll_options(value: List[str]) -> bool:
    if type(value) == list and all(map(lambda x: type(x) == str, value)):
        return True
    else:
        raise ValidationError('poll options must be a list of strings (got ' + repr(value) + ')')

class BasePoll(models.Model):
    uuid: models.UUIDField = models.UUIDField(default = uuid4)
    question: models.CharField = models.CharField(max_length = 2200) # question must be long enough to include the full text of any river description
    options: models.JSONField = models.JSONField(validators = [validate_poll_options])
    expires: models.DateTimeField = models.DateTimeField()
    closed: models.BooleanField = models.BooleanField(default = False)
    vote_kind: models.Model = BaseVote # pyre-ignore[8]
    invalid_option: models.BooleanField = models.BooleanField(default = True)
    # initialise the votes relevant to this poll. needed so we know who's allowed to vote on it. should be called after creating any poll
    def make_votes(self, river) -> None: # pyre-ignore[2] can't import River for this, see next line
        from river.models import RiverMembership # pyre-ignore[21] this is considered bad form, but as far as i can tell necessary to avoid a circular import
        for voter in RiverMembership.objects.filter(river = river):
            self.vote_kind.objects.create(user = voter.user, poll = self, choice = None if self.vote_kind == SingleVote else [])
    @property
    def specific(self) -> Union['SingleChoicePoll', 'MultipleChoicePoll']:
        if hasattr(self, 'multiplechoicepoll'):
            return self.multiplechoicepoll # pyre-ignore[16]
        else:
            return self.singlechoicepoll # pyre-ignore[16]
    def close(self) -> None:
        pass # how?
            
        

class SingleChoicePoll(BasePoll):
    vote_kind = SingleVote # pyre-ignore[15]
    @property
    def current_results(self) -> Dict[str,List[CustomUser]]: # pyre-ignore[11]
        votes = SingleVote.objects.filter(poll = self, choice__isnull = False)
        results = {option:[] for option in self.options}
        if self.invalid_option:
            results['poll is wrong'] = []
        for vote in votes:
            results[self.options[vote.choice - 1] if vote.choice != 0 else 'poll is wrong'].append(vote.user)
        return results
    def check_closed(self) -> bool:
        if self.closed:
            return True
        elif self.expires < timezone.now():
            self.closed = True
            self.close()
            self.save()
            return True
        else:
            vote_nums = sorted([len(SingleVote.objects.filter(poll = self, choice = option)) for option in range(len(self.options)+1)], reverse = True)
            if vote_nums[0] > vote_nums[1] + len(SingleVote.objects.filter(poll = self, choice__isnull = True)):
                # if all remaining votes went to the current second-place option it still wouldn't equal the top option
                self.closed = True
                self.close()
                self.save()
                return True
            else:
                return False

class MultipleChoicePoll(BasePoll):
    vote_kind = MultipleVote # pyre-ignore[15]
    @property
    def current_results(self) -> Dict[str,List[CustomUser]]:
        votes = MultipleVote.objects.filter(~models.Q(choice = []), poll = self)
        results = {option:[] for option in self.options}
        if self.invalid_option:
            results['poll is wrong'] = []
        for vote in votes:
            for choice in vote.choice:
                results[self.options[choice - 1] if choice != 0 else 'poll is wrong'].append(vote.user)
        return results
    def check_closed(self) -> bool:
        if self.closed:
            return True
        elif self.expires < timezone.now():
            self.closed = True
            self.save()
            return True
        else:
            vote_nums = sorted(list(map(len, self.current_results.values())), reverse = True)
            if vote_nums[0] > vote_nums[1] + len(MultipleVote.objects.filter(poll = self, choice = [])):
                # if all remaining votes went to the current second-place option it still wouldn't equal the top option
                self.closed = True
                self.save()
                return True
            else:
                return False
