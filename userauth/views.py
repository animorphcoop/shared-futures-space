from django.shortcuts import render, redirect
from dashboard import views


def profile():
    return redirect(views.dashboard)
