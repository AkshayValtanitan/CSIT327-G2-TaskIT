from django.db import models
from django.contrib.auth.models import User

# class LoginAttempt(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     timestamp = models.DateTimeField(auto_now_add=True)
#     success = models.BooleanField(default=False)

#     def __str__(self):
#         status = "Success" if self.success else "Failed"
#         return f"{self.user.username} - {status} at {self.timestamp}"

class SupabaseUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    supabase_user_id = models.UUIDField(unique=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    last_login = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username


class LoginAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)

    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.user.username} - {status} at {self.timestamp}"
