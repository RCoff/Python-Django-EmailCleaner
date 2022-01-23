from django.views import View
from django.http import JsonResponse

from data.models import EmailStorage
from django_celery_results.models import TaskResult

from gmailautocleaner.celery import app


class ModelTaskStatus(View):
    id = None

    def get(self, request, id):
        self.id = id
        obj = EmailStorage.objects.get(id=self.id)

        return JsonResponse({'result': obj.ready()})


class CeleryTaskResult(View):
    id = None

    def get(self, request, id):
        self.id = id
        result = app.AsyncResult(str(id))

        return JsonResponse({'result': result.ready()})
