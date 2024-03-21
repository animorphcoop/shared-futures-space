from django import forms
from django.contrib.gis.forms import PointField
from django.forms import MultiValueField, HiddenInput

from core.widgets import PrecisionRadioSelect, LocationInput


class LocationField(MultiValueField):
    """Custom multi field to set coordinates, precision, and zoom in one go

    It's because they are related and there is one widget to set them all.
    """

    def __init__(
        self,
        enable_precision=False,
        enable_zoom=False,
    ):
        super().__init__(
            require_all_fields=False,
            widget=LocationInput(
                enable_precision=enable_precision,
                enable_zoom=enable_zoom,
            ),
            fields=[
                # co-ordinates
                PointField(required=True),
                # precision
                forms.BooleanField(
                    required=False,  # required on a boolean field means must be true!
                    disabled=not enable_precision,
                    widget=PrecisionRadioSelect(),
                ),
                # zoom
                forms.FloatField(
                    required=enable_zoom,
                    disabled=not enable_zoom,
                ),
            ],
            label="Location",
        )
        self.enable_precision = enable_precision
        self.enable_zoom = enable_zoom

    def compress(self, data_list):
        location, precision, zoom = data_list or [None, True, 12]
        data = {"location": location}
        if self.enable_precision:
            data["precision"] = precision
        if self.enable_zoom:
            data["zoom"] = zoom
        return data
