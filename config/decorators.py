from functools import wraps

from django.shortcuts import redirect, render


def user_group(user):
    """Naran grupu dahuluk husi utilizador, ka None se la iha grupu."""
    group = user.groups.first()
    return group.name if group else None


def unauthenticated_user(view_func):
    @wraps(view_func)
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper_func


def allowed_users(allowed_roles=()):
    """Permite de'it utilizador ne'ebé nia grupu iha ``allowed_roles``.

    Utilizador seluk simu pajina 403 (la'ós 200) atu log no monitorizasaun
    bele deteta tentativa asesu la autorizadu.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper_func(request, *args, **kwargs):
            if user_group(request.user) in allowed_roles:
                return view_func(request, *args, **kwargs)
            return render(request, 'auth/403.html', status=403)
        return wrapper_func
    return decorator
