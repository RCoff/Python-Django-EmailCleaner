import os

from django.shortcuts import HttpResponseRedirect, reverse
import msal
import requests
from dotenv import load_dotenv

scopes = ['User.Read', 'Mail.Read']


def outlook_sign_in(request):
    flow = get_sign_in_flow()
    request.session['auth_flow'] = flow

    return HttpResponseRedirect(flow['auth_uri'])


def outlook_callback(request):
    result = get_token_from_code(request)
    return HttpResponseRedirect(reverse('outlook-load'))


def load_cache(request):
    cache = msal.SerializableTokenCache()
    if request.session.get('outlook_token_cache'):
        cache.deserialize(request.session['outlook_token_cache'])

    return cache


def save_cache(request, cache):
    if cache.has_state_changed:
        request.session['outlook_token_cache'] = cache.serialize()


def get_msal_app(cache=None):
    # TODO: Check authority uri
    auth_app = msal.ConfidentialClientApplication(
        client_id=os.environ.get('outlook_app_client_id'),
        client_credential=os.environ.get('outlook_app_client_secret_value'),
        token_cache=cache
    )

    return auth_app


def get_sign_in_flow():
    auth_app = get_msal_app()

    return auth_app.initiate_auth_code_flow(
        scopes=scopes,
        redirect_uri=os.environ.get('outlook_redirect_uri')
    )


def get_token_from_code(request):
    cache = load_cache(request)
    auth_app = get_msal_app(cache)

    accounts = auth_app.get_accounts()
    result = None
    if accounts:
        result = auth_app.acquire_token_silent(scopes, account=accounts[0])

    if not result:
        flow = request.session.pop('auth_flow', {})
        result = auth_app.acquire_token_by_auth_code_flow(flow, request.GET)

    save_cache(request, cache)

    return result

