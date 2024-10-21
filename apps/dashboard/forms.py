from area.models import Area
from core.forms import LocationField
from django import forms
from django.conf import settings
from django.core import mail


class ContactForm(forms.Form):
    message = forms.CharField(label="Message", widget=forms.Textarea)
    subject = forms.CharField(label="Subject", max_length=100)
    email = forms.EmailField(label="Email", max_length=100)

    def send_email(self, user):
        subject_dict = {
            "resources": "Suggest resources",
            "feedback": "Send your feedback",
            "rollout": "Enquire about roll out in your area",
            "bug": "Report a bug",
            "postcode": "Change your postcode",
            "other": "Other",
        }
        email_dict = {
            "resources": ["resources@sharedfutures.space"],
            "feedback": ["feedback@sharedfutures.space"],
            "rollout": ["enquire@sharedfutures.space"],
            "bug": ["dev@animorph.coop"],
            "postcode": ["dev@animorph.coop"],
            "other": ["feedback@sharedfutures.space"],
        }
        subject_verbose = subject_dict[self.cleaned_data["subject"]]
        receivers_emails = email_dict[self.cleaned_data["subject"]]
        mail.send_mail(
            subject=f"SFS Contact Form submission from: {user.display_name}",
            message=f"(user id: {user.uuid}, email given: {self.cleaned_data['email']})\n\nsubject: {subject_verbose}\n\n{self.cleaned_data['message']}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=receivers_emails,
        )


class AreaForm(forms.ModelForm):
    post_code = forms.CharField(label="Post Codes")
    location = LocationField(enable_zoom=True)
    zoom = forms.IntegerField(required=False)
    image = forms.ImageField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        location = cleaned_data.get("location")

        if not location:
            raise forms.ValidationError("Location is required.")
        # the "location" field gives us a dict with the multiple values
        # which we can include directly in our cleaned data here
        cleaned_data.update(cleaned_data.pop("location", {}))
        return cleaned_data

    class Meta:
        model = Area
        fields = ["name", "image", "location", "zoom"]
