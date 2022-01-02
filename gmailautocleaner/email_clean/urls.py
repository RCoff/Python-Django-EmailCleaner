from django.urls import path
from . import views


urlpatterns = [
    path('load/gmail', views.load_gmail, name='gmail-load'),
    path('load/outlook', views.load_outlook, name='outlook-load'),
]
