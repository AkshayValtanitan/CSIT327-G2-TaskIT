from django.db import models
import uuid
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
User = get_user_model()

# class Users(models.Model):
#     user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True, max_length=255)
#     username = models.CharField(max_length=255, unique=True)
#     password = models.CharField(max_length=255)
#     google_id = models.CharField(max_length=255, blank=True, null=True)
#     date_created = models.DateTimeField(auto_now_add=True)
#     last_login = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         db_table = 'user_table'

#     def __str__(self):
#         return self.email

# class SupabaseUser(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     supabase_user_id = models.UUIDField(unique=True)
#     email = models.EmailField(unique=True)
#     username = models.CharField(max_length=150)
#     last_login = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return self.username
    
#     User = get_user_model()


class LoginAttempt(models.Model):
    # user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True)
    # user = models.ForeignKey(Users, on_delete=models.CASCADE)
    # timestamp = models.DateTimeField(auto_now_add=True)
    # success = models.BooleanField(default=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    email_or_username = models.CharField(max_length=255, null=True, blank=True)
    success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.user.username} - {status} at {self.timestamp}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    google_id = models.CharField(max_length=255, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username

# class Users(models.Model):
#     user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True, max_length=255)
#     username = models.CharField(max_length=255, unique=True)
#     password = models.CharField(max_length=255)
#     google_id = models.CharField(max_length=255, blank=True, null=True)
#     date_created = models.DateTimeField(auto_now_add=True)
#     last_login = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'users'

#     def __str__(self):
#         return self.email