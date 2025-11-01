# import requests
from django.http import HttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import authenticate, login as auth_login, get_user_model
from django.shortcuts import render, redirect
from allauth.socialaccount.signals import social_account_added
from allauth.account.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from django.contrib import messages
# from taskit_project.supabase_client import supabase
import hashlib
from .models import LoginAttempt
# from .models import Users
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialApp
from django.contrib.auth.hashers import check_password
from django.contrib.sites.models import Site
from .models import Profile
# from login.models import SupabaseUser

# SUPABASE_URL = "https://bwaczilydwpkqlrxdjoq.supabase.co"
# SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ3YWN6aWx5ZHdwa3Fscnhkam9xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTE0MTI0OSwiZXhwIjoyMDc0NzE3MjQ5fQ.RZ5WzeDouz5yNLFyg0W9e9ef8Lol2XnusQguDI4Z-6w"
# SUPABASE_TABLE = "users"

User = get_user_model()

def login_view(request):
    password_error = None
    email_error = None
    username_error = None
    general_error = None

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not password:
            password_error = "Password is required"

        if email and username:
            general_error = "Please use either email or username, not both."
        elif not email and not username:
            general_error = "Please enter either email or username."

        user_obj = None
        if not general_error:
            if email:
                try:
                    user_obj = User.objects.get(email=email)
                except User.DoesNotExist:
                    email_error = "Email not found"
            elif username:
                try:
                    user_obj = User.objects.get(username=username)
                except User.DoesNotExist:
                    username_error = "Username not found"

            if user_obj and check_password(password, user_obj.password):
                # Successful login
                auth_login(request, user_obj)

                # Ensure Profile exists
                profile, created = Profile.objects.get_or_create(user=user_obj)
                profile.last_login = timezone.now()
                profile.save()

                # Save session
                request.session["user_id"] = user_obj.id
                request.session["email"] = user_obj.email
                request.session["username"] = user_obj.username

                messages.success(request, "Logged in successfully!")
                return redirect("/dashboard/")
            elif user_obj:
                password_error = "Invalid password"

    # Google login
    try:
        current_site = Site.objects.get_current(request)
        google_enabled = SocialApp.objects.filter(provider="google", sites=current_site).exists()
    except Exception:
        google_enabled = False

    return render(request, "login.html", {
        "password_error": password_error,
        "email_error": email_error,
        "username_error": username_error,
        "general_error": general_error,
        "google_enabled": google_enabled,
    })

def logout_view(request):
	request.session.flush() 
	messages.success(request, "Logged out successfully.")
	return redirect('login')

# This runs automatically when a user logs in via ANY method, including Google
@receiver(user_logged_in)
def handle_google_login(sender, request, user, **kwargs):
    social_accounts = user.socialaccount_set.filter(provider="google")
    if social_accounts.exists():
        sociallogin = social_accounts.first()
        google_id = sociallogin.uid

        profile, created = Profile.objects.get_or_create(user=user)
        profile.google_id = google_id
        profile.last_login = timezone.now()
        profile.save()

        request.session["user_id"] = user.id
        request.session["email"] = user.email
        request.session["username"] = user.username
        
@receiver(social_account_added)
def link_existing_user(sender, request, sociallogin, **kwargs):
    user = sociallogin.user
    if hasattr(sociallogin, "account") and sociallogin.account:
        profile, created = Profile.objects.update_or_create(
            user=user,
            defaults={
                "google_id": sociallogin.account.uid,
                "last_login": timezone.now()
            }
        )

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # sociallogin.user contains the Google account email
        email_address = sociallogin.user.email
        if not email_address:
            return

        try:
            # Check if a user with this email exists
            user = self.get_user(email=email_address)
            if user:
                # Connect this sociallogin to the existing user
                sociallogin.connect(request, user)
                # Update Profile
                profile, _ = Profile.objects.get_or_create(user=user)
                profile.google_id = sociallogin.uid
                profile.last_login = timezone.now()
                profile.save()
        except Exception:
            pass

# @receiver(user_logged_in)
# def update_last_login_supabase(request, user, **kwargs):

# 	try:
# 		supa_user = Profile.objects.get(user=user)
# 		supa_user.last_login = timezone.now()
# 		supa_user.save(update_fields=['last_login'])
# 	except Profile.DoesNotExist:
# 		print(f"[WARN] SupabaseUser entry missing for {user.username}")
          

# @receiver(user_logged_in)
# def sync_google_user_supabase(request, user, **kwargs):

# 	social_accounts = user.socialaccount_set.filter(provider="google")
# 	if not social_accounts.exists():
# 		return

# 	sociallogin = social_accounts.first()
# 	extra_data = sociallogin.extra_data
# 	email = extra_data.get("email") or user.email

# 	supa_user, created = Profile.objects.update_or_create(
# 		email=email,
# 		defaults={
# 			"user": user,
# 			"first_name": extra_data.get("given_name", ""),
# 			"last_name": extra_data.get("family_name", ""),
# 			"username": extra_data.get("name", f"user{user.id}"),
# 			"google_id": sociallogin.uid,
# 			"last_login": timezone.now(),
# 		}
# 	)

# 	request.session['user_id'] = str(supa_user.supabase_user_id)
# 	request.session['email'] = email
# 	print("DEBUG: Stored user_id in session:", request.session.get("user_id"))

    

# @receiver(user_logged_in)
# def update_last_login_supabase(request, user, **kwargs):
#
#     SUPABASE_URL = "https://bwaczilydwpkqlrxdjoq.supabase.co"
#     SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ3YWN6aWx5ZHdwa3Fscnhkam9xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTE0MTI0OSwiZXhwIjoyMDc0NzE3MjQ5fQ.RZ5WzeDouz5yNLFyg0W9e9ef8Lol2XnusQguDI4Z-6w"
#     SUPABASE_TABLE = "users"
#
#     data = {"last_login": timezone.now().isoformat()}
#
#     response = requests.patch(
#         f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?email=eq.{user.email}",
#         json=data,
#         headers={
#             "apikey": SUPABASE_KEY,
#             "Authorization": f"Bearer {SUPABASE_KEY}",
#             "Content-Type": "application/json",
#             "Prefer": "return=representation",
#         }
#     )
#
#     if response.status_code not in (200, 204):
#         print("Supabase last_login update error:", response.text)
#