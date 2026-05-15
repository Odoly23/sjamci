from django.db.models.signals import post_save
from django.dispatch import receiver
from benefisiariu.models import BeneficiariuEvaluation, Benefisiariu
from custom.models import Status

@receiver(post_save, sender=BeneficiariuEvaluation)
def sync_benef_status(sender, instance, created, **kwargs):
    if created:
        benef = instance.benefisiariu
        try:
            status_obj = Status.objects.get(name=instance.status)
            benef.status = status_obj
            benef.save()
        except Status.DoesNotExist:
            pass