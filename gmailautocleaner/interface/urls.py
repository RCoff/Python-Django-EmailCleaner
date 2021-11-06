from django.contrib import admin
from django.urls import path, include

from . import views
from gmail_clean import main

urlpatterns = [
    path('', views.index, name='index'),
    path('emails/load', views.load_emails, name='load-emails')
]
