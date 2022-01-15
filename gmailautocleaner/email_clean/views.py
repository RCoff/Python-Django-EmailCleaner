from django.shortcuts import render, reverse, HttpResponseRedirect
from email_clean.gmail import main
from email_clean.outlook import get_emails


def load_gmail(request):
    if request.method == 'GET':
        return main.main(request)


def load_outlook(request):
    if request.method == 'GET':
        loaded_emails = get_emails(request)
        return render(request, 'emails.html', context={'loaded_emails': loaded_emails})


def sign_out(request):
    del request.session['credentials']
    del request.session['user_email']
    return HttpResponseRedirect(reverse('index'))
