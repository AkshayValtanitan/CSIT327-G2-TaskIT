from django.dispatch import receiver
from allauth.account.signals import user_logged_in
from django.conf import settings
from taskit_project.supabase_client import supabase_service

SUPABASE_USERS_TABLE = getattr(settings, "SUPABASE_USERS_TABLE", "users")

@receiver(user_logged_in)
def set_supabase_session(sender, request, user, **kwargs):
    """
    When a user logs in (email/password or Google),
    fetch their Supabase user_id and store in session.
    """
    resp = supabase_service.table(SUPABASE_USERS_TABLE).select("user_id").eq("email", user.email).execute()
    data = getattr(resp, "data", [])
    if data:
        supabase_user_id = data[0]["user_id"]
        request.session["supabase_user_id"] = supabase_user_id
        request.session["user_id"] = supabase_user_id
        request.session["email"] = user.email
