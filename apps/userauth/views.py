from django.shortcuts import render
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import CustomUser
from .forms import CustomUserUpdateForm

from .tasks import send_after

from allauth.account.adapter import DefaultAccountAdapter


# TODO: consider redirecting to dashboard which will have a link to profile view
def profile_view(request):
    # return redirect(views.dashboard))
    return render(request, 'account/profile.html')


class CustomUserUpdateView(UpdateView):
    model = CustomUser
    form_class = CustomUserUpdateForm
    success_url = reverse_lazy(profile_view)


class CustomUserDeleteView(DeleteView):
    model = CustomUser
    success_url = reverse_lazy('landing')


# for overriding default email send behaviour: https://stackoverflow.com/a/55965459
class CustomAllauthAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        msg = self.render_mail(template_prefix, email, context)
        send_after.delay(5, msg)
