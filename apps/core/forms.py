from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from formtools.wizard.views import SessionWizardView

from core.widgets import LocationInput, PrecisionRadioSelect
from django import forms
from django.contrib.gis.forms import PointField
from django.forms import MultiValueField


class LocationField(MultiValueField):
    """Custom multi field to set coordinates, precision, and zoom in one go

    It's because they are related and there is one widget to set them all.
    """

    def __init__(
        self,
        enable_precision=False,
        enable_zoom=False,
        marker_type="river",
    ):
        super().__init__(
            require_all_fields=False,
            widget=LocationInput(
                enable_precision=enable_precision,
                enable_zoom=enable_zoom,
                marker_type=marker_type,
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


class SharedFuturesWizardView(SessionWizardView):
    """Shared utilities to make the Wizard views suit our needs"""

    def get(self, request, *args, **kwargs):
        """Support discard and restoring on get

        discard:
            if you add "?discard" to url it will clear storage
            and send you to dashboard

        restoring saved data:
            by default if you reload the form with a GET it'll
            reset the storage, we want to continue where we
            left off, so we treat it as a goto step

        to *not* reset storage if we just get the page again"""
        if "discard" in self.request.GET:
            self.storage.reset()
            return HttpResponseRedirect(reverse_lazy("dashboard"))

        return self.render_goto_step(self.steps.first)

    def post(self, *args, **kwargs):
        if "wizard_save" in self.request.POST:
            self.save_submitted_data()
            return self.render_goto_step(self.steps.current)

        return super().post(*args, **kwargs)

    def render_goto_step(self, goto_step, **kwargs):
        """Save data when jumping to another step, e.g. previous step

        By default, jumping to a step does _not_ save the data for the page you are on.
        We override it to do so as suggested by the docs:

        See https://django-formtools.readthedocs.io/en/latest/wizard.html#formtools.wizard.views.WizardView.render_goto_step

        Inspired by https://stackoverflow.com/a/65099307

        Importantly, it does *not* validate the data when jumping to a step as we
        want to save the data regardless, e.g. when jumping back to the first page, we want to
        still save what was entered on the second page.

        (validation *does* happen when you do next/submit)
        """
        if self.steps.current != goto_step:
            """Only save data if we are actually moving steps

            They are the same if we resubmit the "go to step" form
            e.g. pressing refresh in the browser

            We need to avoid overwriting the storage in that scenario
            """
            self.save_submitted_data()

        return super().render_goto_step(goto_step, **kwargs)

    def save_submitted_data(self):
        """Save the submitted data"""
        form = self.get_form(
            data=self.request.POST,
            files=self.request.FILES,
        )

        self.storage.set_step_data(self.storage.current_step, self.process_step(form))
        self.storage.set_step_files(
            self.storage.current_step,
            self.process_step_files(form),
        )
