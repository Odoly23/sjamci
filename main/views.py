import os
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone

from users.models import AuditLogin


# ══════════════════════════════════════════════════════════════
#  HELPER — ambil IP address dari request
# ══════════════════════════════════════════════════════════════

def _get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _get_user_type(user):
    """Tentukan tipe user berdasarkan group."""
    if user.is_superuser:
        return 'admin'
    groups = user.groups.values_list('name', flat=True)
    if 'cliente' in groups:
        return 'cliente'
    return 'emp'


# ══════════════════════════════════════════════════════════════
#  LOGIN
# ══════════════════════════════════════════════════════════════

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if not username or not password:
            messages.warning(request, 'Username no password labele mamuk.')
            return render(request, 'auth/login.html', {'title': 'Pajina Login'})
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                messages.error(request, 'Konta ne\'e desativadu. Kontaktu administrador.')
                return render(request, 'auth/login.html', {'title': 'Pajina Login'})
            login(request, user)
            AuditLogin.objects.create(
                user       = user,
                ip_address = _get_client_ip(request),
                user_agent = request.META.get('HTTP_USER_AGENT', ''),
                user_type  = _get_user_type(user),
                is_active  = True,
            )
            messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Username ka password salah. Favor koko fila fali.')
    return render(request, 'auth/login.html', {'title': 'Pajina Login'})


# ══════════════════════════════════════════════════════════════
#  LOGOUT
# ══════════════════════════════════════════════════════════════

@login_required
def logout_view(request):
    # ── Update audit logout ───────────────────────────────
    audit = AuditLogin.objects.filter(
        user      = request.user,
        is_active = True
    ).order_by('-login_time').first()

    if audit:
        audit.logout_time = timezone.now()
        audit.duration    = audit.logout_time - audit.login_time
        audit.is_active   = False
        audit.save(update_fields=['logout_time', 'duration', 'is_active'])

    request.session.flush()
    logout(request)
    return redirect('login')


# ══════════════════════════════════════════════════════════════
#  HOME — halaman sambutan semua user
# ══════════════════════════════════════════════════════════════

@login_required
def home(request):
    if not request.user.is_active:
        logout(request)
        return redirect('login')

    group = request.user.groups.all()[0].name if request.user.groups.exists() else None

    context = {
        'group':      group,
        'title':      'Sistema Manajementu',
        'homeactive': 'active',
    }
    return render(request, 'home/home.html', context)


# ══════════════════════════════════════════════════════════════
#  ERROR PAGES
# ══════════════════════════════════════════════════════════════

def error_404(request, exception):
    return render(request, 'auth/404.html', {})

def error_500(request):
    return render(request, 'auth/500.html', {})