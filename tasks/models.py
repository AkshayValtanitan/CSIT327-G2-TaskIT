from django.db import models
from django.contrib.auth.models import User
from login.models import SupabaseUser

class Task(models.Model):
    supabase_task_id = models.UUIDField(unique=True)
    user = models.ForeignKey(SupabaseUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({'Done' if self.completed else 'Pending'})"
