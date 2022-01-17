from django.http import JsonResponse
from django.views import View
from data.models import EmailStorage


class ModifyEmail(View):
    http_method_names = ['patch', 'delete']

    def delete(self, request):
        req_body = request.BODY
        user_emails = EmailStorage.objects.filter(user_email=request.session['user_email'])
        pass

    def patch(self, request):
        req_body = request.BODY
        pass
