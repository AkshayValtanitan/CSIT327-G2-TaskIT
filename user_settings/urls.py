from django.urls import path
from . import views

urlpatterns = [
    path('', views.settings_view, name='settings'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    # path('change_password_view/', views.change_password_view, name='change_password_view'),
    path("send-otp/", views.send_otp_view, name="send_otp"),
]
