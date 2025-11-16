import os
import hashlib
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, get_user_model
from django.utils import timezone
from allauth.account.signals import user_logged_in
from django.dispatch import receiver
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

from taskit_project.supabase_client import supabase_anon, supabase_service
from .models import LoginAttempt

User = get_user_model()
SUPABASE_TABLE = getattr(settings, "SUPABASE_USERS_TABLE", "users")
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_SERVICE_KEY = settings.SUPABASE_SERVICE_KEY
SUPABASE_ANON_KEY = settings.SUPABASE_ANON_KEY


def login_view(request):
    password_error = None
    email_error = None
    username_error = None

    if request.method == "POST":
        password = request.POST.get("password", "").strip()
        email = request.POST.get("email", "").strip()
        username = request.POST.get("username", "").strip()

        if not password:
            password_error = "Password is required"

        if email:
            # get Supabase for email
            resp = supabase_anon.table(SUPABASE_TABLE).select("*").eq("email", email).execute()
            user_data = getattr(resp, "data", []) or []
            if not user_data:
                email_error = "Email not found"
            else:
                row = user_data[0]
                hashed = hashlib.sha256(password.encode()).hexdigest()
                if row.get("password") == hashed:
                    user, _ = User.objects.get_or_create(
                        username=row.get("username") or f"user_{row.get('user_id')}",
                        defaults={"email": row.get("email", "")},
                    )
                    user.set_unusable_password()
                    user.save()
                    auth_login(request, user)

                    LoginAttempt.objects.create(user=user, success=True)

                    request.session["supabase_user_id"] = row.get("user_id")
                    request.session["email"] = row.get("email")
                    request.session["username"] = row.get("username")

                    messages.success(request, "Logged in successfully!")
                    return redirect("/dashboard/")
                else:
                    LoginAttempt.objects.create(email_or_username=email, success=False)
                    password_error = "Invalid password"

        elif username:
            print("Trying username:", username)  # debug
            # resp = supabase_anon.table(SUPABASE_TABLE).select("*").eq("username", username).execute()
            resp = supabase_service.table(SUPABASE_TABLE).select("*").eq("username", username).execute()
            print("Supabase response:", getattr(resp, "data", None))  # debug
            user_data = getattr(resp, "data", []) or []
            if not user_data:
                username_error = "Username not found"
            else:
                row = user_data[0]
                hashed = hashlib.sha256(password.encode()).hexdigest()
                if row.get("password") == hashed:
                    user, _ = User.objects.get_or_create(
                        username=row.get("username") or f"user_{row.get('user_id')}",
                        defaults={"email": row.get("email", "")},
                    )
                    user.set_unusable_password()
                    user.save()
                    auth_login(request, user)

                    LoginAttempt.objects.create(user=user, success=True)

                    request.session["supabase_user_id"] = row.get("user_id")
                    request.session["username"] = row.get("username")

                    messages.success(request, "Logged in successfully!")
                    return redirect("/dashboard/")
                else:
                    LoginAttempt.objects.create(email_or_username=username, success=False)
                    password_error = "Invalid password"
        else:
            messages.error(request, "Please enter either email or username")

    current_site = Site.objects.get_current()
    google_enabled = SocialApp.objects.filter(provider='google', sites=current_site).exists()

    return render(request, "login.html", {
        "password_error": password_error,
        "email_error": email_error,
        "username_error": username_error,
        "google_enabled": google_enabled
    })

def logout_view(request):
    request.session.flush()
    messages.success(request, "Logged out successfully.")
    return redirect("login")


@receiver(user_logged_in)
def update_last_login_supabase(sender, request, user, **kwargs):
    supabase_user_id = request.session.get("supabase_user_id")
    if not supabase_user_id:
        return

    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?user_id=eq.{supabase_user_id}"
    payload = {"last_login": timezone.now().isoformat()}
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    try:
        r = requests.patch(url, json=payload, headers=headers, timeout=10)
        if r.status_code not in (200, 204):
            print("Supabase last_login update error:", r.status_code, r.text)
    except Exception as e:
        print("Supabase last_login patch exception:", str(e))

@receiver(user_logged_in)
def sync_google_user_supabase(sender, request, user, **kwargs):
    social_accounts = user.socialaccount_set.filter(provider="google")
    if not social_accounts.exists():
        return

    sociallogin = social_accounts.first()
    extra_data = sociallogin.extra_data or {}
    email = extra_data.get("email") or user.email

    data = {
        "first_name": extra_data.get("given_name", ""),
        "last_name": extra_data.get("family_name", ""),
        "username": extra_data.get("name", f"user{user.id}"),
        "email": email,
        "password": "",
        "google_id": sociallogin.uid,
        "last_login": timezone.now().isoformat()
    }

    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?on_conflict=email"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

    supabase_user_id = None
    try:
        # Try upsert
        r = requests.post(url, json=data, headers=headers, timeout=10)
        r.raise_for_status()
        res_json = r.json()
        if isinstance(res_json, list) and res_json:
            supabase_user_id = res_json[0].get("user_id")

        # If no user_id returned, fetch existing user by email
        if not supabase_user_id:
            get_url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?email=eq.{email}"
            gr = requests.get(get_url, headers=headers, timeout=10)
            if gr.status_code == 200:
                existing = gr.json()
                if existing:
                    supabase_user_id = existing[0].get("user_id")

        # Finally, store in session for your APIs
        request.session["supabase_user_id"] = supabase_user_id
        request.session["user_id"] = supabase_user_id
        request.session["email"] = email
        request.session["username"] = data.get("username")

        print("Supabase user ID after Google login:", supabase_user_id)

    except Exception as e:
        print("sync_google_user_supabase failed:", str(e))
