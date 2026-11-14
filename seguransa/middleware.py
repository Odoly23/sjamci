import threading

from django.shortcuts import redirect
from django.urls import reverse

_state = threading.local()


def current_request():
    return getattr(_state, 'request', None)


def client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class CurrentRequestMiddleware:
    """Rai request atuál atu rejistu auditoria hatene sé mak halo alterasaun."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _state.request = request
        try:
            return self.get_response(request)
        finally:
            _state.request = None


class ForcePasswordChangeMiddleware:
    """Utilizador ho password temporáriu tenke troka molok uza sistema."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            security = getattr(user, 'security', None)
            if security is not None and security.must_change_password:
                allowed = (reverse('password-change'), reverse('logout'))
                if request.path not in allowed and not request.path.startswith(('/static/', '/media/')):
                    return redirect('password-change')
        return self.get_response(request)
