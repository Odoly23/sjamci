from django.utils import timezone

from .models import ActivityLog, UserSecurity


def require_password_change(user):
    """Marka konta atu obriga troka password iha login tuir mai."""
    security = UserSecurity.for_user(user)
    security.must_change_password = True
    security.save(update_fields=['must_change_password'])


def password_was_changed(user):
    security = UserSecurity.for_user(user)
    security.must_change_password = False
    security.password_changed_at = timezone.now()
    security.save(update_fields=['must_change_password', 'password_changed_at'])


def log_security_event(request, description, target=None):
    """Rejistu eventu seguransa (reset password, 2FA, nst.) iha auditoria."""
    from .middleware import client_ip
    user = request.user if request is not None and request.user.is_authenticated else None
    ActivityLog.objects.create(
        user=user,
        username=user.username if user else '',
        action='security',
        app_label='seguransa',
        model='Konta',
        object_pk=str(target.pk) if target is not None else '',
        object_repr=(f'{description}: {target}' if target is not None else description)[:200],
        ip_address=client_ip(request) if request is not None else None,
        path=request.path[:255] if request is not None else '',
    )
