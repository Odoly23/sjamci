from django.db import models
from django.core.validators import FileExtensionValidator
from config.upload_utils import upload_financial_book
from custom.models import BaseModel, Status
from kni.models import Business


# ============================================================
# HELPER FUNCTION
# ============================================================
def generate_hashed(instance_id):
    import hashlib
    if instance_id:
        return hashlib.blake2b(str(instance_id).encode()).hexdigest()
    return None


class BusinessImpactMonitoring(BaseModel):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='impact_monitorings', verbose_name="Negósiu")
    monitoring_date = models.DateField(verbose_name="Data Monitorizasaun")
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True, blank=True)
    fund_received = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Fundus Simu ($)")
    fund_used = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Fundus Uza Ona ($)")
    fund_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Saldo Restante ($)")
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Rendimentu Fulan Ida ($)")
    monthly_expense = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Despeza Fulan Ida ($)")
    monthly_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Lukru Fulan Ida ($)")
    total_employee = models.IntegerField(default=0, verbose_name="Total Trabalhador")
    use_accounting_book = models.BooleanField(default=False, verbose_name="Uza Livru Kontabilidade")
    has_income = models.BooleanField(default=True, verbose_name="Iha Rendimentu")
    paid_tax = models.BooleanField(default=False, verbose_name="Selu Impostu")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Montante Impostu ($)")
    plan_credit = models.BooleanField(default=False, verbose_name="Planu Atu Simu Kreditu")
    credit_source = models.CharField(max_length=255, blank=True, null=True, verbose_name="Fonte Kreditu")
    plan_new_business = models.BooleanField(default=False, verbose_name="Iha Planu Negósiu Foun")
    new_business_idea = models.TextField(blank=True, null=True, verbose_name="Ideia Negósiu Foun")
    observation = models.TextField(blank=True, null=True, verbose_name="Observasaun")
    hashed = models.CharField(max_length=128, blank=True, null=True, editable=False)

    class Meta:
        verbose_name = "Monitorizasaun Impaktu"
        verbose_name_plural = "Monitorizasaun Impaktu Sira"
        ordering = ['-monitoring_date']

    def __str__(self):
        return f"{self.business} - {self.monitoring_date}"

    def save(self, *args, **kwargs):
        self.fund_balance = (self.fund_received or 0) - (self.fund_used or 0)
        self.monthly_profit = (self.monthly_income or 0) - (self.monthly_expense or 0)
        
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new and not self.hashed:
            self.hashed = generate_hashed(self.id)
            super().save(update_fields=['hashed'])


class FundUsage(BaseModel):
    monitoring = models.ForeignKey(BusinessImpactMonitoring, on_delete=models.CASCADE, related_name='fund_usages', verbose_name="Monitorizasaun")
    item_name = models.CharField(max_length=255, verbose_name="Naran Gastu")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montante ($)")
    description = models.TextField(blank=True, null=True, verbose_name="Deskrisaun")
    hashed = models.CharField(max_length=128, blank=True, null=True, editable=False)

    class Meta:
        verbose_name = "Utilizasaun Fundus"
        verbose_name_plural = "Utilizasaun Fundus Sira"

    def __str__(self):
        return f"{self.item_name} - ${self.amount}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.hashed:
            self.hashed = generate_hashed(self.id)
            super().save(update_fields=['hashed'])


class BusinessAsset(BaseModel):
    CONDITION_CHOICES = (
        ('Diak', 'Diak'),
        ('Aat', 'Aat'),
        ('Lakon', 'Lakon'),
    )
    monitoring = models.ForeignKey(BusinessImpactMonitoring, on_delete=models.CASCADE, related_name='assets', verbose_name="Monitorizasaun")
    asset_name = models.CharField(max_length=255, verbose_name="Naran Asset")
    quantity = models.IntegerField(default=1, verbose_name="Quantidade")
    value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor Asset ($)")
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='Diak', verbose_name="Kondisaun")
    hashed = models.CharField(max_length=128, blank=True, null=True, editable=False)

    class Meta:
        verbose_name = "Asset Negósiu"
        verbose_name_plural = "Asset Negósiu Sira"

    def __str__(self):
        return self.asset_name

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.hashed:
            self.hashed = generate_hashed(self.id)
            super().save(update_fields=['hashed'])


class CashFlow(BaseModel):
    TYPE_CHOICES = (
        ('IN', 'Osan Tama'),
        ('OUT', 'Osan Sai'),
    )
    monitoring = models.ForeignKey(BusinessImpactMonitoring, on_delete=models.CASCADE, related_name='cashflows', verbose_name="Monitorizasaun")
    transaction_date = models.DateField(verbose_name="Data Transasaun")
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="Tipu Transasaun")
    description = models.CharField(max_length=255, verbose_name="Deskrisaun")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montante ($)")
    hashed = models.CharField(max_length=128, blank=True, null=True, editable=False)

    class Meta:
        verbose_name = "Fluxu Osan"
        verbose_name_plural = "Fluxu Osan Sira"

    def __str__(self):
        return f"{self.transaction_type} - ${self.amount}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.hashed:
            self.hashed = generate_hashed(self.id)
            super().save(update_fields=['hashed'])


class FinancialBook(BaseModel):
    monitoring = models.ForeignKey(BusinessImpactMonitoring, on_delete=models.CASCADE, related_name='financial_books', verbose_name="Monitorizasaun")
    title = models.CharField(max_length=200, verbose_name="Naran Dokumentu")
    file = models.FileField(
        upload_to=upload_financial_book,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'xlsx', 'xls'])],
        verbose_name="Anexa Livru Kontabilidade"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Deskrisaun")
    hashed = models.CharField(max_length=128, blank=True, null=True, editable=False)

    class Meta:
        verbose_name = "Livru Kontabilidade"
        verbose_name_plural = "Livru Kontabilidade Sira"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.hashed:
            self.hashed = generate_hashed(self.id)
            super().save(update_fields=['hashed'])