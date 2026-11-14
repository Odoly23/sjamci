from django.contrib.auth.models import User
from django.db import models

from benefisiariu.models import Benefisiariu


class OfflineSubmission(models.Model):
    """Rejistu ida ne'ebé prienxe offline no sinkroniza tiha ona.

    ``uuid`` mai husi dispozitivu; garante katak rejistu ida la rai dala rua
    maski dispozitivu haruka fali (ezemplu rede kotu iha klaran).
    """
    uuid = models.UUIDField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offline_submissions')
    module = models.CharField(max_length=10)
    benefisiariu = models.ForeignKey(Benefisiariu, null=True, blank=True, on_delete=models.SET_NULL)
    filled_at = models.DateTimeField(null=True, blank=True, verbose_name='Prienxe iha dispozitivu')
    synced_at = models.DateTimeField(auto_now_add=True, verbose_name='Sinkroniza')

    class Meta:
        ordering = ['-synced_at']
        verbose_name = 'Rejistu Offline'
        verbose_name_plural = 'Rejistu Offline'

    def __str__(self):
        return f'{self.module} {self.uuid}'
