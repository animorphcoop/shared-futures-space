from django.shortcuts import render, redirect, get_object_or_404
from dashboard import views
from .forms import CustomUserUpdateForm


def profile():
    return redirect(views.dashboard)

