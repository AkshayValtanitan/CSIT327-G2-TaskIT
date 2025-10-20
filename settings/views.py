from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

SUPABASE_URL = "https://bwaczilydwpkqlrxdjoq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ3YWN6aWx5ZHdwa3Fscnhkam9xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTE0MTI0OSwiZXhwIjoyMDc0NzE3MjQ5fQ.RZ5WzeDouz5yNLFyg0W9e9ef8Lol2XnusQguDI4Z-6w"
SUPABASE_TABLE = "users"

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