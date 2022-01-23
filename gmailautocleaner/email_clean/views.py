from django.shortcuts import render, reverse, redirect
from django.contrib.auth import logout
from email_clean.gmail import main
from email_clean.outlook import get_emails
from django.contrib.auth.decorators import login_required


@login_required(login_url='/auth/gmail/sign-in')
def load_gmail(request):
    if request.method == 'GET':
        return main.main(request)


def load_outlook(request):
    if request.method == 'GET':
        loaded_emails = get_emails(request)
        return render(request, 'emails.html', context={'loaded_emails': loaded_emails})


def sign_out(request):
    if request.session.get('credentials'):
        del request.session['credentials']
    if request.session.get('user_email'):
        del request.session['user_email']
    logout(request)

    return redirect(reverse('index'))
