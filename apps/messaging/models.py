# pyre-strict

import re
from django.utils import timezone
from django.utils.html import escape
from django.db import models
from uuid import uuid4

class Message(models.Model):
    uuid: models.UUIDField = models.UUIDField(default = uuid4, editable = False)
    timestamp: models.DateTimeField = models.DateTimeField(default=timezone.now)
    sender: models.ForeignKey = models.ForeignKey('userauth.CustomUser', null = True, on_delete = models.SET_NULL)
    text: models.CharField = models.CharField(max_length = 2000, blank=True)
    image: models.ImageField = models.ImageField(upload_to='messages/images/', blank=True)
    file: models.FileField = models.FileField(upload_to='messages/files/', blank=True)
    snippet: models.CharField = models.CharField(max_length = 2000, default = '')
    reply_to: models.ForeignKey = models.ForeignKey('messaging.Message', null=True, on_delete = models.SET_NULL)
    chat: models.ForeignKey = models.ForeignKey('messaging.Chat', on_delete = models.CASCADE)
    hidden: models.BooleanField = models.BooleanField(default = False)
    hidden_reason: models.CharField = models.CharField(max_length = 25, null = True, default = None)
    # context_* values are nullable fields used to fill in the gaps in system messages
    context_action: models.ForeignKey = models.ForeignKey('action.Action', null = True, on_delete = models.SET_NULL)
    context_river: models.ForeignKey = models.ForeignKey('river.River', null = True, on_delete = models.SET_NULL)
    context_user_a: models.ForeignKey = models.ForeignKey('userauth.CustomUser', null = True, on_delete = models.SET_NULL, related_name = 'user_a')
    context_user_b: models.ForeignKey = models.ForeignKey('userauth.CustomUser', null = True, on_delete = models.SET_NULL, related_name = 'user_b')
    context_bool: models.BooleanField = models.BooleanField(default=False)
    context_poll: models.ForeignKey = models.ForeignKey('poll.BasePoll', null = True, on_delete = models.SET_NULL)

    @property
    def text_with_links(self) -> str:
        """
        This function replaces all URLs in the message with HTML anchor links.
        Regex from https://stackoverflow.com/a/3809435
        """
        text = escape(self.text)
        url_regex = re.compile(r"""
            (?:
                (?:https?)  # match the URL scheme (http or https)
                :\/\/       # match the colon slash combo ://
            )?              # make URL scheme optional (eg. www.example.com instead of https://www.example.com)
            [\w/\-?=%.]+    # match one or more alphanumeric characters, slashes, hyphens, question marks, equal signs, percent signs, dots
            \.              # match a literal dot
            [\w/\-?=%.]+    # match one or more alphanumeric characters, slashes, hyphens, question marks, equal signs, percent signs, dots
        """, re.VERBOSE)

        chars_added = 0  # keep track of new characters we add
        for match in url_regex.finditer(text):
            start, end = match.span()
            link_in_html = f'<a href="{match.group()}" target="_blank" style="text-decoration: underline;">{match.group()}</a>'
            text = text[:start+chars_added] + link_in_html + text[end+chars_added:]

            # character length of the url that already exists in text
            url_length = len(match.group())

            # We need to calculate how many characters we have added because they
            # change the offset (match.span()) of the subsequent links that we need to replace.
            chars_added += len(link_in_html) - url_length

        return text

    def flagged(self, user) -> None: # pyre-ignore[2]
        from userauth.models import CustomUser # pyre-ignore[21] don't like it but there's so many things defined in terms of each other
        existing = Flag.objects.filter(message = self, flagged_by = user)
        if len(existing) == 0:
            f = Flag.objects.create(message = self, flagged_by = user)
            if len(Flag.objects.filter(message = self)) >= 3:
                   self.hidden = True
                   self.hidden_reason = "due to flagging by users"
                   self.save()
        else:
            existing[0].delete()
            if len(Flag.objects.filter(message = self)) < 3:
                   self.hidden = False
                   self.save()

class Chat(models.Model):
    uuid: models.UUIDField = models.UUIDField(default = uuid4, editable = False)

class Flag(models.Model):
    message: models.ForeignKey = models.ForeignKey(Message, on_delete = models.CASCADE)
    flagged_by: models.ForeignKey = models.ForeignKey('userauth.CustomUser', on_delete = models.SET_NULL, null = True)
