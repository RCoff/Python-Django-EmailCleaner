from django.urls import path
import gmail_clean.outlook.auth as outlook_auth


urlpatterns = [
    path('outlook/callback', outlook_auth.outlook_callback, name='outlook-callback'),
    path('outlook/sign-in', outlook_auth.outlook_sign_in, name='outlook-sign-in'),
]
