from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

SUPABASE_URL = "https://bwaczilydwpkqlrxdjoq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ3YWN6aWx5ZHdwa3Fscnhkam9xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTE0MTI0OSwiZXhwIjoyMDc0NzE3MjQ5fQ.RZ5WzeDouz5yNLFyg0W9e9ef8Lol2XnusQguDI4Z-6w"
SUPABASE_TABLE = "users"

User = get_user_model()

@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'dashboard.html')