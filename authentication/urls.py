# authentication/urls.py
from django.urls import path
from .views import login_view
from .views import password_reset_request, password_reset_confirm, verify_2fa, resend_2fa_code

urlpatterns = [
    path('login/', login_view, name='login'),
     path('password/reset/', password_reset_request, name='password_reset_request'),
     path('verify_2fa/', verify_2fa, name='verify_2fa'),
     path('resend-2fa-code/', resend_2fa_code, name='resend-2fa-code'),
    path('password/reset/confirm/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
]
