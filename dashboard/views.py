from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

User = get_user_model()

@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'dashboard.html')


@login_required(login_url='login')
def settings_view(request):
    return render(request, 'settings.html')
