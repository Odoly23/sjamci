from django.contrib.auth.models import User
from django.db import models


class UserSecurity(models.Model):
    """Estadu seguransa ba konta ida: troka password obrigatóriu no 2FA."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='security')
    must_change_password = models.BooleanField(default=False, verbose_name='Tenke troka password')
    password_changed_at = models.DateTimeField(null=True, blank=True, verbose_name='Password troka ikus')
    totp_secret = models.CharField(max_length=64, blank=True, default='')
    totp_enabled = models.BooleanField(default=False, verbose_name='Verifikasaun pasu-2 ativu')
    totp_last_step = models.BigIntegerField(default=0)

    class Meta:
        verbose_name = 'Seguransa Konta'
        verbose_name_plural = 'Seguransa Konta'

    def __str__(self):
        return f'Seguransa: {self.user.username}'

    @classmethod
    def for_user(cls, user):
        obj, _ = cls.objects.get_or_create(user=user)
        return obj


class ActivityLog(models.Model):
    """Rejistu auditoria: sé mak kria, altera ka hamoos dadus saida no bainhira."""
    ACTIONS = [
        ('create', 'Kria'),
        ('update', 'Altera'),
        ('delete', 'Hamoos'),
        ('security', 'Seguransa'),
    ]
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Data')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='activity_logs')
    username = models.CharField(max_length=150, blank=True, default='')
    action = models.CharField(max_length=10, choices=ACTIONS, db_index=True, verbose_name='Asaun')
    app_label = models.CharField(max_length=50, blank=True, default='')
    model = models.CharField(max_length=80, blank=True, default='', db_index=True, verbose_name='Tabela')
    object_pk = models.CharField(max_length=64, blank=True, default='')
    object_repr = models.CharField(max_length=200, blank=True, default='', verbose_name='Dadus')
    changes = models.JSONField(default=dict, blank=True, verbose_name='Alterasaun')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='Enderesu IP')
    path = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        ordering = ['-created_at', '-id']
        verbose_name = 'Rejistu Atividade'
        verbose_name_plural = 'Rejistu Atividade'

    def __str__(self):
        return f'{self.created_at:%d/%m/%Y %H:%M} {self.username} {self.action} {self.model}'
