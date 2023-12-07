from django import template
from django.utils.text import slugify

register = template.Library()


@register.simple_tag
def user_chat_slug(chat, *args):
    if not chat.user:
        raise Exception('missing "user" field on chat')
    user = chat.user
    return slugify(" ".join([user.display_name, str(user.pk)]))
