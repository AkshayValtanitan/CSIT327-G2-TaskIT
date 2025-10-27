from django.urls import path
from .views import create_superuser
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("login/", views.login_view, name="login"),
    # path("register/", views.register_view, name="register"),
    # path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path("create-superuser/", create_superuser),
    # path('api/tasks/', views.tasks_api, name='tasks_api'),
    # path('api/tasks/<str:task_id>/', views.task_detail_api, name='task_detail_api'),
    # path("login/github/", views.github_login, name="github-login"),
    # path("github/callback/", views.github_callback, name="github-callback"), <----Not working for now
]
