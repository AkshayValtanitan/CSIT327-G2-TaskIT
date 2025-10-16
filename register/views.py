from django.contrib.auth import login, get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from taskit_project.supabase_client import supabase
import hashlib  
import uuid
from .forms import RegisterForm

SUPABASE_URL = "https://bwaczilydwpkqlrxdjoq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ3YWN6aWx5ZHdwa3Fscnhkam9xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTE0MTI0OSwiZXhwIjoyMDc0NzE3MjQ5fQ.RZ5WzeDouz5yNLFyg0W9e9ef8Lol2XnusQguDI4Z-6w"
SUPABASE_TABLE = "users"

User = get_user_model()

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            first_name = data["first_name"]
            last_name = data["last_name"]
            username = data["username"]
            email = data["email"]
            password = data["password"]
            confirm_password = data["confirm_password"]
            google_id = request.POST.get("google_id") or None

            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, "register.html", {"form": form})

            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            user_id = str(uuid.uuid4())

            response = supabase.table("users").insert({
                "user_id": user_id,
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "email": email,
                "password": hashed_password,
                "google_id": google_id
            }).execute()

            if response.data:
                messages.success(request, "Account created successfully! Please log in.")
                return redirect("login")
            else:
                messages.error(request, "Error creating account. Try again.")
        else:
            messages.error(request, "Please fill in all required fields.")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})