import csv
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from config.decorators import allowed_users, user_group
from kni.utils import generate_qrcode_base64

from . import totp
from .models import ActivityLog, UserSecurity
from .utils import log_security_event, password_was_changed

PENDING_KEY = 'pending_2fa'
PENDING_TTL = 5 * 60      # segundu
MAX_2FA_ATTEMPTS = 5


# ══════════════════════════════════════════════════════════════
#  TROKA PASSWORD
# ══════════════════════════════════════════════════════════════
@login_required
def password_change(request):
    security = UserSecurity.for_user(request.user)
    form = PasswordChangeForm(request.user, request.POST or None)
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        password_was_changed(user)
        log_security_event(request, 'Troka password', user)
        messages.success(request, 'Password troka ho susesu.')
        return redirect('home')
    return render(request, 'seguransa/password_change.html', {
        'form': form,
        'forced': security.must_change_password,
        'group': user_group(request.user),
        'title': 'Troka Password',
    })


# ══════════════════════════════════════════════════════════════
#  VERIFIKASAUN PASU-2 (2FA / TOTP)
# ══════════════════════════════════════════════════════════════
@login_required
def two_factor_settings(request):
    security = UserSecurity.for_user(request.user)
    context = {'security': security, 'group': user_group(request.user), 'title': 'Verifikasaun Pasu-2'}

    if not security.totp_enabled:
        if not security.totp_secret:
            security.totp_secret = totp.new_secret()
            security.save(update_fields=['totp_secret'])
        if request.method == 'POST':
            step = totp.matching_step(security.totp_secret, request.POST.get('code'))
            if step:
                security.totp_enabled = True
                security.totp_last_step = step
                security.save(update_fields=['totp_enabled', 'totp_last_step'])
                log_security_event(request, 'Ativa verifikasaun pasu-2', request.user)
                messages.success(request, 'Verifikasaun pasu-2 ativu ona.')
                return redirect('two-factor')
            messages.error(request, 'Kódigu la loos. Favor koko fali.')
        uri = totp.provisioning_uri(security.totp_secret, request.user.username)
        context.update(qr=generate_qrcode_base64(uri), secret=security.totp_secret)
    return render(request, 'seguransa/two_factor.html', context)


@login_required
@require_POST
def two_factor_disable(request):
    security = UserSecurity.for_user(request.user)
    if not request.user.check_password(request.POST.get('password', '')):
        messages.error(request, 'Password la loos.')
        return redirect('two-factor')
    security.totp_enabled = False
    security.totp_secret = ''
    security.totp_last_step = 0
    security.save(update_fields=['totp_enabled', 'totp_secret', 'totp_last_step'])
    log_security_event(request, 'Desativa verifikasaun pasu-2', request.user)
    messages.warning(request, 'Verifikasaun pasu-2 desativa ona.')
    return redirect('two-factor')


def start_two_factor(request, user):
    """Bolu husi login: rai utilizador iha espera to'o kódigu verifika."""
    request.session[PENDING_KEY] = {'user_id': user.pk, 'at': time.time(), 'attempts': 0}


def two_factor_verify(request):
    """Pasu daruak login nian: husu kódigu husi aplikasaun autentikadór."""
    from main.views import complete_login

    pending = request.session.get(PENDING_KEY)
    if not pending or time.time() - pending['at'] > PENDING_TTL:
        request.session.pop(PENDING_KEY, None)
        messages.warning(request, 'Sesaun verifikasaun remata. Favor login fali.')
        return redirect('login')

    user = get_user_model().objects.filter(pk=pending['user_id'], is_active=True).first()
    if user is None:
        request.session.pop(PENDING_KEY, None)
        return redirect('login')

    if request.method == 'POST':
        security = UserSecurity.for_user(user)
        step = totp.matching_step(security.totp_secret, request.POST.get('code'), security.totp_last_step)
        if step:
            security.totp_last_step = step
            security.save(update_fields=['totp_last_step'])
            request.session.pop(PENDING_KEY, None)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return complete_login(request, user)
        pending['attempts'] += 1
        request.session[PENDING_KEY] = pending
        if pending['attempts'] >= MAX_2FA_ATTEMPTS:
            request.session.pop(PENDING_KEY, None)
            messages.error(request, 'Kódigu sala dala barak. Favor login fali.')
            return redirect('login')
        messages.error(request, 'Kódigu la loos. Favor koko fali.')
    return render(request, 'seguransa/two_factor_verify.html', {'title': 'Verifikasaun Pasu-2'})


# ══════════════════════════════════════════════════════════════
#  REJISTU ATIVIDADE (AUDITORIA)
# ══════════════════════════════════════════════════════════════
def _filtered_logs(request):
    logs = ActivityLog.objects.all()
    params = request.GET
    if params.get('user'):
        logs = logs.filter(username__icontains=params['user'].strip())
    if params.get('action'):
        logs = logs.filter(action=params['action'])
    if params.get('model'):
        logs = logs.filter(model__icontains=params['model'].strip())
    if params.get('from'):
        logs = logs.filter(created_at__date__gte=params['from'])
    if params.get('to'):
        logs = logs.filter(created_at__date__lte=params['to'])
    return logs


@login_required
@allowed_users(allowed_roles=['admin'])
def activity_log_list(request):
    logs = _filtered_logs(request)
    page = Paginator(logs, 50).get_page(request.GET.get('page'))
    query = request.GET.copy()
    query.pop('page', None)
    return render(request, 'seguransa/activity_log.html', {
        'page': page,
        'total': logs.count(),
        'actions': ActivityLog.ACTIONS,
        'query': query.urlencode(),
        'group': user_group(request.user),
        'title': 'Rejistu Atividade',
        'legend': 'Rejistu Atividade (Auditoria)',
    })


@login_required
@allowed_users(allowed_roles=['admin'])
def activity_log_export(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="rejistu_atividade.csv"'
    response.write('﻿')
    writer = csv.writer(response)
    writer.writerow(['Data', 'Utilizador', 'Asaun', 'Tabela', 'ID', 'Dadus', 'Alterasaun', 'IP', 'Pajina'])
    for log in _filtered_logs(request)[:20000].iterator():
        writer.writerow([log.created_at.strftime('%Y-%m-%d %H:%M:%S'), log.username, log.get_action_display(),
                         log.model, log.object_pk, log.object_repr,
                         '; '.join(f'{k}: {v[0]} → {v[1]}' for k, v in log.changes.items()),
                         log.ip_address or '', log.path])
    log_security_event(request, 'Esporta rejistu atividade')
    return response


# ══════════════════════════════════════════════════════════════
#  HEALTH CHECK — ba monitorizasaun servidór
# ══════════════════════════════════════════════════════════════
def healthz(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        database = 'ok'
    except Exception:  # noqa: BLE001
        database = 'error'
    status = 200 if database == 'ok' else 503
    return JsonResponse({'status': 'ok' if status == 200 else 'error', 'database': database}, status=status)
