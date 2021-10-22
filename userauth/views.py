from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy

from dashboard import views
from .models import CustomUser
from .forms import CustomUserUpdateForm


# TODO: consider redirecting to dashboard which will have a link to profile view
def profile_view(request):
    # return redirect(views.dashboard)
    return render(request, 'account/profile.html')


class CustomUserUpdateView(UpdateView):
    model = CustomUser
    form_class = CustomUserUpdateForm


class CustomUserDeleteView(DeleteView):
    model = CustomUser
    success_url = reverse_lazy('landing')
