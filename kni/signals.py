from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum

from benefisiariu.models import BeneficiariuEvaluation, Benefisiariu
from custom.models import Status, Bussines_size
from .models import Employee, Business


@receiver(post_save, sender=BeneficiariuEvaluation)
def sync_benef_status(sender, instance, created, **kwargs):
    if created and instance.status:
        benef = instance.benefisiariu
        try:
            status_obj = Status.objects.get(name=instance.status)
            benef.status = status_obj
            benef.save()
        except Status.DoesNotExist:
            pass


@receiver(post_save, sender=Employee)
@receiver(post_delete, sender=Employee)
def update_business_size(sender, instance, **kwargs):
    business = instance.business
    if not business:
        return
    aggregate_result = Employee.objects.filter(business=business).aggregate(total_pekerja=Sum('total'))
    total = aggregate_result['total_pekerja'] or 0
    if 0 <= total <= 5:
        kode = "Mo"
    elif 6 <= total <= 20:
        kode = "SM"
    elif 21 <= total <= 50:
        kode = "MD"
    else:
        kode = "GD"

    try:
        size = Bussines_size.objects.get(code=kode)
    except Bussines_size.DoesNotExist:
        size = None

    if business.size_id != (size.id if size else None):
        Business.objects.filter(pk=business.pk).update(size=size)