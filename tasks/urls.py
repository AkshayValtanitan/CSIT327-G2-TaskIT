from django.urls import path
from . import views

urlpatterns = [
    path('tasks/', views.tasks_api, name='tasks_api'),
    path('tasks/<uuid:task_id>/', views.task_detail_api, name='task_detail_api'),
    path('tasks/summary/', views.weekly_summary_api, name='weekly_summary_api'),
    path('tasks/weekly_completion_stats/', views.weekly_completion_stats_api, name='weekly_completion_stats'),
]
