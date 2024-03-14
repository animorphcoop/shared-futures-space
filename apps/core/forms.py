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
                    disabled=not enable_precision,
                    required=enable_precision,
                    widget=PrecisionRadioSelect(),
                ),
                # zoom
                forms.FloatField(
                    disabled=not enable_zoom,
                    required=enable_zoom,
                ),
            ],
            label="Location",
        )

    def compress(self, data_list):
        return data_list
