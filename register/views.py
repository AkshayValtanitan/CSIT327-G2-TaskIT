import hashlib
import uuid
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, get_user_model
from django.utils import timezone
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

from .forms import RegisterForm
from taskit_project.supabase_client import supabase_service
from login.models import Profile

User = get_user_model()
SUPABASE_TABLE = "users"
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_SERVICE_KEY = settings.SUPABASE_SERVICE_KEY


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

            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
            else:
                # hash password for storage
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                user_id = str(uuid.uuid4())

                # Prepare Supabase payload
                payload = {
                    "user_id": user_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "username": username,
                    "email": email,
                    "password": hashed_password,
                    "last_login": timezone.now().isoformat(),
                }

                url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
                headers = {
                    "apikey": SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",  # returns inserted row
                }

                try:
                    r = requests.post(url, json=payload, headers=headers, timeout=10)
                    r.raise_for_status()
                    res_json = r.json()
                    if isinstance(res_json, list) and res_json:
                        supabase_user_id = res_json[0].get("user_id")

                        # Create local Django user for session management
                        user, _ = User.objects.get_or_create(
                            username=username,
                            defaults={"email": email, "first_name": first_name, "last_name": last_name},
                        )
                        user.set_unusable_password()  # we rely on Supabase
                        user.save()

                        Profile.objects.create(user=user, last_login=None)

                        messages.success(request, "Account created successfully! Please log in.")
                        return redirect("login")
                    else:
                        messages.error(request, "Error creating account. Try again.")
                except Exception as e:
                    print("Supabase registration error:", e)
                    messages.error(request, "Error creating account. Try again.")
        else:
            messages.error(request, "Please fill in all required fields.")
    else:
        form = RegisterForm()

    # Check if Google login is enabled
    try:
        current_site = Site.objects.get_current(request)
        google_enabled = SocialApp.objects.filter(provider="google", sites=current_site).exists()
    except Exception:
        google_enabled = False

    return render(request, "register.html", {"form": form, "google_enabled": google_enabled})
