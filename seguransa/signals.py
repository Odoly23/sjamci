"""Rejistu automátiku ba kria/altera/hamoos dadus iha aplikasaun lokál."""
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .middleware import client_ip, current_request
from .models import ActivityLog

AUDITED_APPS = {'benefisiariu', 'kni', 'suave', 'manufatureira', 'mpms', 'monitoring',
                'custom', 'users', 'auth'}
EXCLUDED_MODELS = {'users.auditlogin', 'auth.permission'}
HIDDEN_FIELDS = {'password', 'last_login', 'updated_at', 'updated_by', 'totp_secret'}
MAX_VALUE = 120


def _audited(sender):
    meta = sender._meta
    return meta.app_label in AUDITED_APPS and meta.label_lower not in EXCLUDED_MODELS


def _text(value):
    return '' if value is None else str(value)[:MAX_VALUE]


def _snapshot(instance):
    data = {}
    for field in instance._meta.concrete_fields:
        if field.name in HIDDEN_FIELDS:
            continue
        data[field.name] = _text(field.value_from_object(instance))
    return data


def _write(instance, action, changes=None):
    request = current_request()
    user = getattr(request, 'user', None) if request is not None else None
    if user is not None and not user.is_authenticated:
        user = None
    meta = instance._meta
    try:
        representation = str(instance)
    except Exception:  # noqa: BLE001 — __str__ balu depende ba relasaun ne'ebé hamoos ona
        representation = f'{meta.object_name} #{instance.pk}'
    ActivityLog.objects.create(
        user=user,
        username=user.username if user else '',
        action=action,
        app_label=meta.app_label,
        model=meta.object_name,
        object_pk=str(instance.pk),
        object_repr=representation[:200],
        changes=changes or {},
        ip_address=client_ip(request) if request is not None else None,
        path=request.path[:255] if request is not None else '',
    )


@receiver(pre_save)
def remember_previous_state(sender, instance, raw=False, **kwargs):
    if raw or not _audited(sender) or instance.pk is None:
        return
    previous = sender._default_manager.filter(pk=instance.pk).first()
    instance._audit_before = _snapshot(previous) if previous is not None else None


@receiver(post_save)
def log_save(sender, instance, created, raw=False, **kwargs):
    if raw or not _audited(sender):
        return
    before = getattr(instance, '_audit_before', None)
    if created or before is None:
        _write(instance, 'create')
        return
    after = _snapshot(instance)
    changes = {name: [before.get(name, ''), value] for name, value in after.items()
               if before.get(name, '') != value}
    if changes:
        _write(instance, 'update', changes)


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if _audited(sender):
        _write(instance, 'delete')
