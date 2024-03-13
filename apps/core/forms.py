from django import forms
from django.contrib.gis.forms import PointField
from django.forms import MultiValueField

from core.widgets import PrecisionRadioSelect, LocationAndPrecisionInput


class LocationAndPrecisionField(MultiValueField):
    """Custom multi field to set coordinates and precision in one go

    It's because they are related and there is one widget to set both.
    """

    def __init__(self):
        super().__init__(
            widget=LocationAndPrecisionInput(),
            fields=[
                forms.BooleanField(widget=PrecisionRadioSelect()),
                PointField(),
            ],
            label="Location",
        )

    def compress(self, data_list):
        return data_list


class LocationAndZoomField(MultiValueField):
    """Custom multi field to set coordinates and zoom in one go

    It's because they are related and there is one widget to set both.
    """

    def __init__(self):
        super().__init__(
            widget=LocationAndPrecisionInput(),
            fields=[
                forms.fields.IntegerField(),
                PointField(),
            ],
            label="Location",
        )

    def compress(self, data_list):
        return data_list
