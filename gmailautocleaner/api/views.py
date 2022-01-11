from django.views import View
from django.http import JsonResponse

from gmailautocleaner.celery import app


# Create your views here.
class CeleryTaskResult(View):
    task_id = None

    def get(self, request, task_id: str):
        self.task_id = task_id
        result = app.AsyncResult(str(task_id))
        print(result.ready())

        return JsonResponse({'result': result.ready()})
