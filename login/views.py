# import requests
from django.http import HttpResponse
from django.contrib.auth import login as auth_login, get_user_model
from django.shortcuts import render, redirect
from allauth.account.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from django.contrib import messages
# from taskit_project.supabase_client import supabase
import hashlib
from .models import Users, SupabaseUser, LoginAttempt
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# SUPABASE_URL = "https://bwaczilydwpkqlrxdjoq.supabase.co"
# SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ3YWN6aWx5ZHdwa3Fscnhkam9xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTE0MTI0OSwiZXhwIjoyMDc0NzE3MjQ5fQ.RZ5WzeDouz5yNLFyg0W9e9ef8Lol2XnusQguDI4Z-6w"
# SUPABASE_TABLE = "users"

User = get_user_model()

# def create_superuser(request):
#     User = get_user_model()
#     if not User.objects.filter(username="shanenathan").exists():
#         User.objects.create_superuser(
#             username="shanenathan",
#             email="shanenathanarchival@gmail.com",
#             password="123456"
#         )
#         return HttpResponse("Superuser created successfully!")
#     else:
#         return HttpResponse("Superuser already exists.")

# def login_view(request):
#     password_error = None
#     email_error = None
#     username_error = None
#
#     if request.method == "POST":
#         password = request.POST.get("password", "").strip()
#         email = request.POST.get("email", "").strip()
#         username = request.POST.get("username", "").strip()
#
#         if not password:
#             password_error = "Password is required"
#
#         # LOGIN BY EMAIL
#         if email:
#             response = supabase.table("users").select("*").eq("email", email).execute()
#             user_data = response.data
#             if user_data:
#                 if user_data[0]["password"] == hashlib.sha256(password.encode()).hexdigest():
#
#                     # Create or fetch the Django user
#                     user, created = User.objects.get_or_create(
#                         username=user_data[0]["username"],
#                         defaults={"email": email},
#                     )
#                     if created:
#                         user.set_password(password)
#                         user.save()
#
#                     # Log in the Django user (for @login_required)
#                     auth_login(request, user)
#                     LoginAttempt.objects.create(user=user, success=True)
#
#                     # Store additional info in session if needed
#                     request.session['user_id'] = user_data[0]['user_id']
#                     request.session['email'] = user_data[0]['email']
#
#                     supabase_user_id = user_data[0]["user_id"]
#                     SupabaseUser.objects.update_or_create(
#                         user=user,
#                         defaults={
#                             "supabase_user_id": supabase_user_id,
#                             "email": user_data[0]["email"],
#                             "username": user_data[0]["username"],
#                             "last_login": timezone.now(),
#                         },
#                     )
#
#                     messages.success(request, "Logged in successfully!")
#                     return redirect("/dashboard/")
#
#                     # request.session['user_id'] = user_data[0]['user_id']
#                     # request.session['email'] = user_data[0]['email']
#                     # messages.success(request, "Logged in successfully!")
#                     # return redirect("/dashboard")
#                 else:
#                     LoginAttempt.objects.create(email_or_username=email, success=False)
#                     password_error = "Invalid password"
#             else:
#                 email_error = "Email not found"
#         elif username:
#             response = supabase.table("users").select("*").eq("username", username).execute()
#             user_data = response.data
#             # LOGIN BY USERNAME
#             if user_data:
#                 if user_data[0]["password"] == hashlib.sha256(password.encode()).hexdigest():
#
#                     user, created = User.objects.get_or_create(
#                         username=username,
#                         defaults={"email": user_data[0].get("email", "")},
#                     )
#                     if created:
#                         user.set_password(password)
#                         user.save()
#
#                     auth_login(request, user)
#                     LoginAttempt.objects.create(user=user, success=True)
#
#                     request.session['user_id'] = user_data[0]['user_id']
#                     request.session['username'] = user_data[0]['username']
#
#                     supabase_user_id = user_data[0]["user_id"]
#                     SupabaseUser.objects.update_or_create(
#                         user=user,
#                         defaults={
#                             "supabase_user_id": supabase_user_id,
#                             "email": user_data[0]["email"],
#                             "username": user_data[0]["username"],
#                             "last_login": timezone.now(),
#                         },
#                     )
#
#                     messages.success(request, "Logged in successfully!")
#                     return redirect("/dashboard/")
#
#                     # request.session['user_id'] = user_data[0]['user_id']
#                     # request.session['username'] = user_data[0]['username']
#                     # messages.success(request, "Logged in successfully!")
#                     # return redirect("/dashboard")
#                 else:
#                     LoginAttempt.objects.create(email_or_username=username, success=False)
#                     password_error = "Invalid password"
#             else:
#                 username_error = "Username not found"
#         else:
#             messages.error(request, "Please enter either email or username")
#
#     return render(request, "login.html", {
#         "password_error": password_error,
#         "email_error": email_error,
#         "username_error": username_error
#     })

def login_view(request):
	password_error = None
	email_error = None
	username_error = None
	general_error = None

	if request.method == "POST":
		password = request.POST.get("password", "").strip()
		email = request.POST.get("email", "").strip()
		username = request.POST.get("username", "").strip()

		if not password:
			password_error = "Password is required"

		if email and username:
			general_error = "Please use either email or username, not both."
		elif not email and not username:
			general_error = "Please enter either email or username."

		user_data = None

		if not general_error:
			if email:
				try:
					user_data = Users.objects.get(email=email)
				except Users.DoesNotExist:
					email_error = "Email not found"

			elif username:
				try:
					user_data = Users.objects.get(username=username)
				except Users.DoesNotExist:
					username_error = "Username not found"

			if user_data and password:
				hashed_password = hashlib.sha256(password.encode()).hexdigest()
				if user_data.password == hashed_password:
					user, created = User.objects.get_or_create(
						username=user_data.username,
						defaults={"email": user_data.email}
					)
					if created:
						user.set_password(password)
						user.save()

					auth_login(request, user)

					supa_user, _ = SupabaseUser.objects.update_or_create(
						user=user,
						defaults={
							"supabase_user_id": user_data.user_id,
							"email": user_data.email,
							"username": user_data.username,
							"last_login": timezone.now(),
						}
					)

					user_data.last_login = timezone.now()
					user_data.save(update_fields=["last_login"])

					LoginAttempt.objects.create(user=user, success=True)

					request.session["user_id"] = str(user_data.user_id)
					request.session["email"] = user_data.email
					request.session["username"] = user_data.username

					messages.success(request, "Logged in successfully!")
					return redirect("/dashboard/")
				else:
					password_error = "Invalid password"
					if 'user' in locals():
						LoginAttempt.objects.create(user=user, success=False)

	# detect if Google social app is configured for the current site
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

@receiver(user_logged_in)
def update_last_login_supabase(request, user, **kwargs):
	from django.utils import timezone
	from login.models import SupabaseUser

	try:
		supa_user = SupabaseUser.objects.get(user=user)
		supa_user.last_login = timezone.now()
		supa_user.save(update_fields=['last_login'])
	except SupabaseUser.DoesNotExist:
		print(f"[WARN] SupabaseUser entry missing for {user.username}")


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

@receiver(user_logged_in)
def sync_google_user_supabase(request, user, **kwargs):
	from django.utils import timezone
	from login.models import SupabaseUser

	social_accounts = user.socialaccount_set.filter(provider="google")
	if not social_accounts.exists():
		return

	sociallogin = social_accounts.first()
	extra_data = sociallogin.extra_data
	email = extra_data.get("email") or user.email

	supa_user, created = SupabaseUser.objects.update_or_create(
		email=email,
		defaults={
			"user": user,
			"first_name": extra_data.get("given_name", ""),
			"last_name": extra_data.get("family_name", ""),
			"username": extra_data.get("name", f"user{user.id}"),
			"google_id": sociallogin.uid,
			"last_login": timezone.now(),
		}
	)

	request.session['user_id'] = str(supa_user.supabase_user_id)
	request.session['email'] = email
	print("DEBUG: Stored user_id in session:", request.session.get("user_id"))

