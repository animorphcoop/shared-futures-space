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
    Precision and Zoom are both optional

    The current_user bit is slightly funky so worth explaining.

    We use it in this widget to set the default map center/zoom
    to their area.

    It needs to be passed down through many layers to get
    down to the widget template file.

    To get it from the view all the way you need to override:

    - "get_form_kwargs" in the view to include current_user
      see RiverStartWizardView for example

    - the form constructor, to receive the current_user
      see CreateRiverFormStep2 for example

    - pass it to the widget context
      see this class for example

    By default, we set it to None so the widget still works
    if you don't need the current_user
    """

    template_name = "river/widgets/location.html"

    def __init__(
        self, attrs=None, enable_precision=False, enable_zoom=False, marker_type="river"
    ):
        self.enable_precision = enable_precision
        self.enable_zoom = enable_zoom
        self.marker_type = marker_type
        self.current_user = None

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
        context["widget"]["marker_type"] = self.marker_type
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
