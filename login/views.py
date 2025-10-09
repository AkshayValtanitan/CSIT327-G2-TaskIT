import requests
from django.contrib.auth import login as auth_login, get_user_model
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
import json
from allauth.socialaccount.signals import social_account_added
from django.contrib.auth.decorators import login_required
from allauth.account.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from django.contrib import messages
from taskit_project.supabase_client import supabase
from django.views.decorators.csrf import csrf_exempt
import hashlib
import uuid

SUPABASE_URL = "https://bwaczilydwpkqlrxdjoq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ3YWN6aWx5ZHdwa3Fscnhkam9xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTE0MTI0OSwiZXhwIjoyMDc0NzE3MjQ5fQ.RZ5WzeDouz5yNLFyg0W9e9ef8Lol2XnusQguDI4Z-6w"
SUPABASE_TABLE = "users"

User = get_user_model()

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

                    # Create or fetch the Django user
                    user, created = User.objects.get_or_create(
                        username=user_data[0]["username"],
                        defaults={"email": email, "password": password},
                    )

                    # Log in the Django user (for @login_required)
                    auth_login(request, user)

                    # Store additional info in session if needed
                    request.session['user_id'] = user_data[0]['user_id']
                    request.session['email'] = user_data[0]['email']

                    messages.success(request, "Logged in successfully!")
                    return redirect("/dashboard/")

                    # request.session['user_id'] = user_data[0]['user_id']
                    # request.session['email'] = user_data[0]['email']
                    # messages.success(request, "Logged in successfully!")
                    # return redirect("/dashboard")
                else:
                    password_error = "Invalid password"
            else:
                email_error = "Email not found"
        elif username:
            response = supabase.table("users").select("*").eq("username", username).execute()
            user_data = response.data
            if user_data:
                if user_data[0]["password"] == hashlib.sha256(password.encode()).hexdigest():

                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={"email": user_data[0].get("email", ""), "password": password},
                    )

                    auth_login(request, user)

                    request.session['user_id'] = user_data[0]['user_id']
                    request.session['username'] = user_data[0]['username']

                    messages.success(request, "Logged in successfully!")
                    return redirect("/dashboard/")

                    # request.session['user_id'] = user_data[0]['user_id']
                    # request.session['username'] = user_data[0]['username']
                    # messages.success(request, "Logged in successfully!")
                    # return redirect("/dashboard")
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



@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def tasks_api(request):
    """
    GET: return list of tasks for the logged-in user, optionally filtered by year & month.
    POST: create a new task for the logged-in user.
    """
    user_id = request.session.get('user_id') or str(request.user.id)
    print(f"DEBUG: tasks_api user_id from session: {user_id}")
    if not user_id:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    if request.method == "GET":
        year = request.GET.get('year')
        month = request.GET.get('month')  # 0-based from JS
        query = supabase.table("task").select("*").eq("user_id", user_id)
        if year is not None and month is not None:
            try:
                y = int(year)
                m = int(month) + 1
                start = f"{y}-{m:02d}-01"
                if m == 12:
                    end = f"{y+1}-01-01"
                else:
                    end = f"{y}-{m+1:02d}-01"
                query = query.gte("date", start).lt("date", end)
            except ValueError:
                pass
        response = query.order("date").order("hour").execute()
        return JsonResponse({"tasks": response.data or []})

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    title = (payload.get("title") or "").strip()
    date = payload.get("date")
    hour = payload.get("hour")
    color = payload.get("color") or "#2e7d32"
    description = payload.get("description") or ""
    priority = payload.get("priority") or None
    status_val = payload.get("status") or "pending"

    if not title:
        return JsonResponse({"error": "Title is required"}, status=400)
    if not date:
        return JsonResponse({"error": "Date is required"}, status=400)
    if hour is None or str(hour) == "":
        return JsonResponse({"error": "Hour is required"}, status=400)

    task_id = str(uuid.uuid4())
    insert_data = {
        "id": task_id,
        "user_id": user_id,
        "title": title,
        "description": description,
        "date": date,
        "hour": int(hour),
        "color": color,
        "priority": priority,
        "status": status_val,
    }
    resp = supabase.table("task").insert(insert_data).execute()
    if not resp.data:
        return JsonResponse({"error": "Failed to create task"}, status=500)
    return JsonResponse({"task": resp.data[0]})


@login_required(login_url='login')
@require_http_methods(["GET", "PATCH", "DELETE"])
def task_detail_api(request, task_id: str):
    user_id = request.session.get('user_id') or str(request.user.id)
    if not user_id:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    # Ensure the task belongs to the user
    if request.method == "GET":
        resp = supabase.table("task").select("*").eq("id", task_id).eq("user_id", user_id).single().execute()
        if not resp.data:
            return JsonResponse({"error": "Not found"}, status=404)
        return JsonResponse({"task": resp.data})

    if request.method == "PATCH":
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except Exception:
            return HttpResponseBadRequest("Invalid JSON")
        update_fields = {}
        for key in ["title", "description", "date", "hour", "color", "priority", "status"]:
            if key in payload and payload[key] is not None:
                update_fields[key] = payload[key]
        if not update_fields:
            return JsonResponse({"error": "No fields to update"}, status=400)
        resp = supabase.table("task").update(update_fields).eq("id", task_id).eq("user_id", user_id).execute()
        if not resp.data:
            return JsonResponse({"error": "Update failed"}, status=500)
        return JsonResponse({"task": resp.data[0]})

    # DELETE
    resp = supabase.table("task").delete().eq("id", task_id).eq("user_id", user_id).execute()
    return JsonResponse({"ok": True})