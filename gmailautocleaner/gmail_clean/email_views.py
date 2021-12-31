from django.shortcuts import render
from gmail_clean import main
from gmail_clean.outlook import get_emails


def load_gmail(request):
    if request.method == 'GET':
        loaded_emails = main.main(request.session)
        return render(request, 'emails.html', context={'loaded_emails': loaded_emails})


def load_outlook(request):
    if request.method == 'GET':
        loaded_emails = get_emails(request)
        return render(request, 'emails.html', context={'loaded_emails': loaded_emails})
