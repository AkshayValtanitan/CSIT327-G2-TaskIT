from django.shortcuts import render, redirect
from django.contrib import messages
from taskit_project.supabase_client import supabase
import hashlib
import uuid

def login_view(request):
    password_error = None
    email_error = None

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Query Supabase users table (check to see if exists)
        response = supabase.table("users").select("*").eq("email", email).execute()
        user_data = response.data

        if user_data:
            if user_data[0]["password"] == hashed_password:
                # successful login
                request.session['user_id'] = user_data[0]['user_id']
                request.session['email'] = user_data[0]['email']
                messages.success(request, "Logged in successfully!")
                return redirect("/dashboard")
            else:
                # email correct but wrong password
                password_error = "Invalid password"
        else:
            # email not found
            email_error = "Email not found"

    return render(request, "login.html", {
        "password_error": password_error,
        "email_error": email_error
    })

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

def dashboard_view(request):
    if not request.session.get('user_id'):
        messages.error(request, "Please log in first.")
        return redirect('login')
    return render(request, 'dashboard.html')

def logout_view(request):
    request.session.flush() 
    messages.success(request, "Logged out successfully.")
    return redirect('login')

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
#<a href="{% url 'github-login' %}" class="github-btn">Login with GitHub</a>