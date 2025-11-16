from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from .models import Profile
from django.utils import timezone
from taskit_project.supabase_client import supabase_service  # <-- add this

SUPABASE_USERS_TABLE = getattr(settings, "SUPABASE_USERS_TABLE", "users")

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email_address = sociallogin.user.email
        if not email_address:
            return

        try:
            user = self.get_user(email=email_address)
            if user:
                sociallogin.connect(request, user)

                # Update or create profile
                if hasattr(sociallogin, "account") and sociallogin.account:
                    profile, _ = Profile.objects.get_or_create(user=user)
                    profile.google_id = sociallogin.account.uid
                    profile.last_login = timezone.now()
                    profile.save()

                # Fetch Supabase user_id for this email
                resp = supabase_service.table(SUPABASE_USERS_TABLE).select("user_id").eq("email", email_address).execute()
                data = getattr(resp, "data", [])
                if data:
                    supabase_user_id = data[0]["user_id"]
                    request.session["supabase_user_id"] = supabase_user_id
                    request.session["user_id"] = supabase_user_id
                    request.session["email"] = email_address

        except Exception:
            pass
