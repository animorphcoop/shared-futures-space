from django.forms import (
    TextInput,
    HiddenInput,
    MultiWidget,
    NumberInput,
    CheckboxInput,
    RadioSelect,
)

from river.util import get_resource_tags


class PrecisionRadioSelect(RadioSelect):
    def __init__(self):
        super().__init__(
            choices=[
                (True, "My location is exact"),
                (False, "My location is approximate"),
            ]
        )


class LocationInput(MultiWidget):
    """Widget to set precision and coordinates at once

    Goes hand-in-hand with LocationField
    """

    template_name = "river/widgets/location.html"

    def __init__(self, attrs=None):
        _widgets = (
            PrecisionRadioSelect(),
            HiddenInput(),
        )
        super().__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            return value
        return [True, None]


class TagsInput(HiddenInput):
    template_name = "river/widgets/tags.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["tags"] = get_resource_tags()
        return context


widgets = {
    "location_input": LocationInput,
    "tags_input": TagsInput,
}
