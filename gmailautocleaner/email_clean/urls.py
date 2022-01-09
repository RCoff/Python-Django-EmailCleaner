from django.urls import path
from . import views
from .gmail.views import Display

urlpatterns = [
    path('gmail/load', views.load_gmail, name='gmail-load'),
    path('gmail/<uuid:id>', Display.as_view(), name='gmail-display'),
    path('outlook/load', views.load_outlook, name='outlook-load'),
]
