from django.forms import (
    HiddenInput,
)

from river.util import get_resource_tags


class TagsInput(HiddenInput):
    template_name = "river/widgets/tags.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["tags"] = get_resource_tags()
        return context


