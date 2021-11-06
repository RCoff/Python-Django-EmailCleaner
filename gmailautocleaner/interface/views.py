from django.shortcuts import render
from gmail_clean import main


# Create your views here.
def index(request):
    if request.method == 'GET':
        return render(request, 'index.html')


def load_emails(request):
    if request.method == 'GET':
        loaded_emails = main.main(request.session)
        return render(request, 'index.html', context={'loaded_emails': loaded_emails})
