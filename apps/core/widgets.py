from django.forms import RadioSelect, MultiWidget, HiddenInput

from river.widgets import TagsInput


class PrecisionRadioSelect(RadioSelect):
    def __init__(self):
        super().__init__(
            choices=[
                (True, "My location is exact"),
                (False, "My location is approximate"),
            ]
        )


class LocationAndPrecisionInput(MultiWidget):
    """Widget to set coordinates and precision at once

    Goes hand-in-hand with LocationAndPrecisionField
    """

    template_name = "river/widgets/location_and_precision.html"

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


widgets = {
    "location_input": LocationAndPrecisionInput,
    "tags_input": TagsInput,
}
