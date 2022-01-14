from django.views import View
from django.http import JsonResponse

from data.models import EmailStorage

from gmailautocleaner.celery import app


class ModelTaskStatus(View):
    id = None

    def get(self, request, id):
        self.id = id
        obj = EmailStorage.objects.get(id=self.id)

        return JsonResponse({'result': obj.ready()})


# Create your views here.
class CeleryTaskInspectBase:
    app_inspect = app.control.inspect()

    def scheduled(self):
        return self.app_inspect.scheduled()

    def active(self):
        return self.app_inspect.active()

    def reserved(self):
        return self.app_inspect.reserved()

    def inspect_dict(self):
        return {'scheduled': len(self.scheduled()),
                'active': len(self.active()),
                'reserved': len(self.reserved())}


class CeleryTaskResult(View, CeleryTaskInspectBase):
    task_id = None

    def get(self, request, task_id: str):
        self.task_id = task_id
        result = app.AsyncResult(str(task_id))

        return JsonResponse({'result': result.ready()})


class CeleryTaskInspect(View, CeleryTaskInspectBase):

    def get(self, request):
        return JsonResponse(self.inspect_dict())
