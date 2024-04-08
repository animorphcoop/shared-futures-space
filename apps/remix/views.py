from django.shortcuts import render
from django.views.generic import TemplateView


class RemixView(TemplateView):
    template_name = "remix/remix.html"
