import requests
from django.shortcuts import render, redirect
from allauth.socialaccount.signals import social_account_added
from django.contrib.auth.decorators import login_required
from allauth.account.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from django.contrib import messages
from taskit_project.supabase_client import supabase
import hashlib
import uuid

SUPABASE_URL = "https://bwaczilydwpkqlrxdjoq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ3YWN6aWx5ZHdwa3Fscnhkam9xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTE0MTI0OSwiZXhwIjoyMDc0NzE3MjQ5fQ.RZ5WzeDouz5yNLFyg0W9e9ef8Lol2XnusQguDI4Z-6w"
SUPABASE_TABLE = "users"

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
            response = supabase.table("users").select("*").eq("email", email).execute()
            user_data = response.data
            if user_data:
                if user_data[0]["password"] == hashlib.sha256(password.encode()).hexdigest():
                    request.session['user_id'] = user_data[0]['user_id']
                    request.session['email'] = user_data[0]['email']
                    messages.success(request, "Logged in successfully!")
                    return redirect("/dashboard")
                else:
                    password_error = "Invalid password"
            else:
                email_error = "Email not found"
        elif username:
            response = supabase.table("users").select("*").eq("username", username).execute()
            user_data = response.data
            if user_data:
                if user_data[0]["password"] == hashlib.sha256(password.encode()).hexdigest():
                    request.session['user_id'] = user_data[0]['user_id']
                    request.session['username'] = user_data[0]['username']
                    messages.success(request, "Logged in successfully!")
                    return redirect("/dashboard")
                else:
                    password_error = "Invalid password"
            else:
                username_error = "Username not found"
        else:
            messages.error(request, "Please enter either email or username")

    return render(request, "login.html", {
        "password_error": password_error,
        "email_error": email_error,
        "username_error": username_error
    })

def register_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        google_id = request.POST.get("google_id") or None

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html")

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

    return render(request, "register.html")

@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'dashboard.html')

def logout_view(request):
    request.session.flush() 
    messages.success(request, "Logged out successfully.")
    return redirect('login')

@receiver(user_logged_in)
def update_last_login_supabase(request, user, **kwargs):

    SUPABASE_URL = "https://bwaczilydwpkqlrxdjoq.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ3YWN6aWx5ZHdwa3Fscnhkam9xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTE0MTI0OSwiZXhwIjoyMDc0NzE3MjQ5fQ.RZ5WzeDouz5yNLFyg0W9e9ef8Lol2XnusQguDI4Z-6w"
    SUPABASE_TABLE = "users"

    data = {"last_login": timezone.now().isoformat()}

    response = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?email=eq.{user.email}",
        json=data,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
    )

    if response.status_code not in (200, 204):
        print("Supabase last_login update error:", response.text)

@receiver(user_logged_in)
def sync_google_user_supabase(request, user, **kwargs):
    import requests
    from django.utils import timezone

    # Only handle users with a Google account
    social_accounts = user.socialaccount_set.filter(provider="google")
    if not social_accounts.exists():
        return

    sociallogin = social_accounts.first()
    extra_data = sociallogin.extra_data

    email = extra_data.get("email") or user.email or sociallogin.user.emails

    data = {
        "first_name": extra_data.get("given_name", ""),
        "last_name": extra_data.get("family_name", ""),
        "username": extra_data.get("name", f"user{user.id}"),
        "email": email,
        "password": "",  # Google login, no password
        "google_id": sociallogin.uid,
        "last_login": timezone.now().isoformat()
    }

    # Upsert user: insert new or update existing by email
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?on_conflict=email",
        json=data,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    )

    if response.status_code not in (200, 201):
        print("Supabase upsert error:", response.text)
    else:
        print("Google user synced with Supabase:", user.email)

    # Save info in session
    request.session['user_id'] = str(user.id)
    request.session['email'] = email


# def dashboard_view(request):
#     if not request.session.get('user_id'):
#         messages.error(request, "Please log in first.")
#         return redirect('login')
#     return render(request, 'dashboard.html')

# def github_login(request):
#     response = supabase.auth.sign_in_with_oauth({"provider": "github"})
#     return redirect(response.url)

# def github_callback(request):
#     code = request.GET.get("code")
    
#     if code:
#         session = supabase.auth.exchange_code_for_session(code)        <-------------Not working for now
#         user = session.user 
        
#         request.session['user_id'] = user.id
#         request.session['email'] = user.email
        
#         messages.success(request, "Logged in with GitHub successfully!")
#         return redirect("/dashboard")
#     else:
#         messages.error(request, "GitHub login failed")
#         return redirect("/login")


# def login_view(request):
#     password_error = None
#     email_error = None
#     username_error = None

#     if request.method == "POST":
#         password = request.POST.get("password")
#         hashed_password = hashlib.sha256(password.encode()).hexdigest()

#         email = request.POST.get("email")
#         username = request.POST.get("username")
        
#         if email:
#             response = supabase.table("users").select("*").eq("email", email).execute()
#             user_data = response.data
#             if user_data:
#                 if user_data[0]["password"] == hashed_password:
#                     request.session['user_id'] = user_data[0]['user_id']
#                     request.session['email'] = user_data[0]['email']
#                     messages.success(request, "Logged in successfully!")
#                     return redirect("/dashboard")
#                 else:
#                     password_error = "Invalid password"
#             else:
#                 email_error = "Email not found"

#         elif username:
#             response = supabase.table("users").select("*").eq("username", username).execute()
#             user_data = response.data
#             if user_data:
#                 if user_data[0]["password"] == hashed_password:
#                     request.session['user_id'] = user_data[0]['user_id']
#                     request.session['username'] = user_data[0]['username']
#                     messages.success(request, "Logged in successfully!")
#                     return redirect("/dashboard")
#                 else:
#                     password_error = "Invalid password"
#             else:
#                 username_error = "Username not found"

#     return render(request, "login.html", {
#         "password_error": password_error,
#         "email_error": email_error,
#         "username_error": username_error
#     })



#<a href="{% url 'github-login' %}" class="github-btn">Login with GitHub</a>
# <img src="{% static 'login/images/login_bg.jpg' %}" alt="backgroundimage" width="300" height="200">


# <!-- <button type="button" class="github-signin">
#                     <img src="{% static 'login/images/github_logo.png' %}" alt="GitHub Logo">
#                     GitHub
#                 </button> -->