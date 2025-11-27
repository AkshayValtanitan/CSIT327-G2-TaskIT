from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from taskit_project.supabase_client import supabase_service
from supabase import create_client
from django.contrib import messages
import hashlib
import random
from django.core.mail import send_mail

User = get_user_model()

SUPABASE_TABLE = getattr(settings, "SUPABASE_OTPS_TABLE", "users")
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_SERVICE_KEY = settings.SUPABASE_SERVICE_KEY
SUPABASE_ANON_KEY = settings.SUPABASE_ANON_KEY

def supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# @login_required(login_url='login')
# def settings_view(request):
#     # Persist theme preference in session for server-rendered pages
#     if request.method == 'POST':
#         theme = (request.POST.get('theme') or '').strip().lower()
#         if theme in ('light', 'dark'):
#             request.session['theme'] = theme
#         return redirect('settings')

#     current_theme = request.session.get('theme', 'light')
#     return render(request, 'settings.html', { 'current_theme': current_theme })

@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'dashboard.html')


@login_required(login_url='login')
def send_otp_view(request):
    user_id = request.session.get("supabase_user_id")
    if not user_id:
        messages.error(request, "User not recognized.")
        return redirect("settings")

    # Get user's email from Supabase
    resp = supabase_service.table("users").select("email").eq("user_id", user_id).execute()
    row = getattr(resp, "data", [])[0]
    email = row.get("email")
    if not email:
        messages.error(request, "No email registered. Please set your email first.")
        return redirect("settings")

    # Generate OTP
    otp = str(random.randint(100000, 999999))

    # save OTP in Supabase
    supabase_service.table("users").update({"otp": otp}).eq("user_id", user_id).execute()

    # send OTP via on email
    send_mail(
        "Your OTP Code",
        f"Your OTP is: {otp}",
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )

    request.session["otp_email"] = email
    request.session["otp_sent"] = True

    messages.success(request, f"OTP sent to {email}")
    return redirect("settings")


@login_required(login_url='login')
def settings_view(request):
    current_theme = request.session.get('theme', 'light')
    user_id = request.session.get("supabase_user_id")

    if request.method == "POST":
        # Theme update
        if "theme" in request.POST:
            theme = request.POST.get("theme", "").lower()
            if theme in ("light", "dark"):
                request.session["theme"] = theme
            return redirect("settings")

        # Password change process
        otp = request.POST.get("otp", "").strip()
        new_password = request.POST.get("new_password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()
        email = request.session.get("otp_email")

        if not otp or not new_password or not confirm_password:
            messages.error(request, "All fields are required to change password")
            return redirect("settings")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("settings")

        # Verify OTP in Supabase
        otp_resp = supabase_service.table(SUPABASE_TABLE).select("*")\
            .eq("user_id", user_id).eq("otp", otp).execute()
        otp_data = getattr(otp_resp, "data", []) or []

        if not otp_data:
            messages.error(request, "Invalid OTP")
            return redirect("settings")

        # Update password and clear OTP
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        supabase_service.table(SUPABASE_TABLE).update({
            "password": hashed_password,
            "otp": None,
        }).eq("user_id", user_id).execute()

        # Clear email from session
        # del request.session["otp_email"]
        if "otp_email" in request.session:
            del request.session["otp_email"]
        if "otp_sent" in request.session:
            del request.session["otp_sent"]

        messages.success(request, "Password changed successfully!")
        return redirect("settings")

    return render(request, "settings.html", {"current_theme": current_theme})
