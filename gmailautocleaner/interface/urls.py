from django.contrib import admin
from django.urls import path, include

from . import views
from email_clean.gmail import main

urlpatterns = [
    path('', views.index, name='index'),
]
