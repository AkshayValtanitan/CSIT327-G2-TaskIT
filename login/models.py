from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone

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

class Users(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, max_length=255)
    password = models.CharField(max_length=255)
    google_id = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)
    username = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'users'

    def __str__(self):
        return self.email
