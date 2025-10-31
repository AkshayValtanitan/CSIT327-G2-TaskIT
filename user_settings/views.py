from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

User = get_user_model()

@login_required(login_url='login')
def settings_view(request):
    # Persist theme preference in session for server-rendered pages
    if request.method == 'POST':
        theme = (request.POST.get('theme') or '').strip().lower()
        if theme in ('light', 'dark'):
            request.session['theme'] = theme
        return redirect('settings')

    current_theme = request.session.get('theme', 'light')
    return render(request, 'settings.html', { 'current_theme': current_theme })

@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'dashboard.html')