from django.shortcuts import render, redirect
from django.contrib import messages
from taskit_project.supabase_client import supabase
import hashlib
import uuid

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Hash the password (same algorithm used when storing)
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Query Supabase users table
        response = supabase.table("users").select("*").eq("email", email).execute()
        user_data = response.data

        if user_data and user_data[0]["password"] == hashed_password:
            # Successful login
            request.session['user_id'] = user_data[0]['user_id']
            request.session['email'] = user_data[0]['email']
            return redirect("/dashboard")  # replace with your actual dashboard URL
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "login.html")

def register_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
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