from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    # path("login/github/", views.github_login, name="github-login"),
    # path("github/callback/", views.github_callback, name="github-callback"), <----Not working for now
]
