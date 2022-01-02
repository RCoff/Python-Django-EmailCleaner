from django.urls import path
from . import email_views


urlpatterns = [
    path('load/gmail', email_views.load_gmail, name='gmail-load'),
    path('load/outlook', email_views.load_outlook, name='outlook-load'),
]
