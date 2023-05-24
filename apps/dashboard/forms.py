from django import forms
from django.core import mail
from django.conf import settings


class ContactForm(forms.Form):
    message = forms.CharField(label="Message", widget=forms.Textarea)
    subject = forms.CharField(label="Subject", max_length=100)
    email = forms.EmailField(label="Email", max_length=100)

    def send_email(self):
        subject_dict = {
            "resources": "Suggest resources",
            "feedback": "Send your feedback",
            "rollout": "Enquire about roll out in your area",
            "bug": "Report a bug",
        }
        email_dict = {
            "resources": ["resources@sharedfutures.space"],
            "feedback": ["feedback@sharedfutures.space"],
            "rollout": ["enquire@sharedfutures.space"],
            "bug": ["dev@animorph.coop"],
        }
        subject_verbose = subject_dict[self.cleaned_data["subject"]]
        receivers_emails = email_dict[self.cleaned_data["subject"]]
        mail.send_mail(
            subject=f"SFS Contact Form submission from: {self.cleaned_data['email']}",
            message=subject_verbose + "\n\n" + self.cleaned_data["message"],
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=receivers_emails,
        )
