from django.urls import path
import email_clean.outlook.auth as outlook_auth
import email_clean.gmail.auth as gmail_auth
from .views import sign_out

urlpatterns = [
    path('sign-out/', sign_out, name='sign-out'),
    path('outlook/callback', outlook_auth.outlook_callback, name='outlook-callback'),
    path('outlook/sign-in', outlook_auth.outlook_sign_in, name='outlook-sign-in'),
    path('gmail/callback', gmail_auth.gmail_callback, name='gmail-callback'),
    path('gmail/sign-in', gmail_auth.gmail_sign_in, name='gmail-sign-in')
]
