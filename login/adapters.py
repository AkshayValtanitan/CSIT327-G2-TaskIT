from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from .models import Profile
from django.utils import timezone

User = get_user_model()


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email_address = sociallogin.user.email
        if not email_address:
            return

        try:
            user = self.get_user(email=email_address)
            if user:
                sociallogin.connect(request, user)

                if hasattr(sociallogin, "account") and sociallogin.account:
                    profile, _ = Profile.objects.get_or_create(user=user)
                    profile.google_id = sociallogin.account.uid
                    profile.last_login = timezone.now()
                    profile.save()
        except Exception:
            pass