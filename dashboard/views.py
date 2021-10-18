from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='/account/login/')  # redirect when user is not logged in
def dashboard(request):
    return render(request, 'dashboard/dashboard.html')
