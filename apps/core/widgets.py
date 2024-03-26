from django.forms import HiddenInput, MultiWidget, RadioSelect
from river.widgets import TagsInput


class PrecisionRadioSelect(RadioSelect):
    def __init__(self):
        super().__init__(
            choices=[
                (True, "My location is exact"),
                (False, "My location is approximate"),
            ]
        )


class LocationInput(MultiWidget):
    """Widget to set coordinates, precision, and zoom at once

    Goes hand-in-hand with LocationField
    Precision and zoom are both optional
    """

    template_name = "river/widgets/location.html"

    def __init__(self, attrs=None, enable_precision=False, enable_zoom=False):
        self.enable_precision = enable_precision
        self.enable_zoom = enable_zoom
        super().__init__(
            widgets=(
                # co-ordinates
                HiddenInput(),
                # precision
                PrecisionRadioSelect(),
                # zoom
                HiddenInput(),
            ),
            attrs=attrs,
        )

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["enable_precision"] = self.enable_precision
        context["widget"]["enable_zoom"] = self.enable_zoom
        if self.current_user:
            context["widget"]["current_user"] = self.current_user
        return context

    def decompress(self, value):
        if value:
            return value
        return [None, True, 12]


widgets = {
    "location_input": LocationInput,
    "tags_input": TagsInput,
}
