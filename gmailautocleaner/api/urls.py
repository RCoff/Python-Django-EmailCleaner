from django.urls import path
from . import views

urlpatterns = [
    path('task/<uuid:task_id>', views.CeleryTaskResult.as_view(), name='task-status'),
]
