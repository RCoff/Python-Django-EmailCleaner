from django.urls import path
from . import views

urlpatterns = [
    path('task/<uuid:id>/status', views.CeleryTaskResult.as_view(), name='task-status'),
    path('emails/load/<uuid:id>/status', views.ModelTaskStatus.as_view(), name='task-model-status'),
]
