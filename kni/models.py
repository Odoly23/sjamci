import hashlib
from django.db import models
from benefisiariu.models import Benefisiariu
from django.utils import timezone
from custom.models import BaseModel, Status, Municipality, AdministrativePost, Village, Bussines_size, Category_Emp, TIpu_Programa, Sector, Faze,\
							Year, Tipu_Apoio, Tipu_Fundus_Kapital
from config.upload_utils import upload_estado, upload_photo
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User, Group


class Business(BaseModel):
    benefisiariu = models.ForeignKey( Benefisiariu,on_delete=models.CASCADE, verbose_name="Benefisiariu / Sira ne'ebé simu", related_name="negosiu")
    category = models.ForeignKey(Category_Emp, on_delete=models.CASCADE, null=True, blank=True)
    size = models.ForeignKey(Bussines_size, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100,verbose_name="Naran Negósiu", null=True, blank=True)
    idea = models.CharField(max_length=100,verbose_name="Ideia Negósiu", null=True, blank=True)
    sector = models.ForeignKey(Sector,on_delete=models.CASCADE,null=True, verbose_name="Sector Prinsipal", blank=True)
    hashed = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.benefisiariu} - {self.idea}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            Business.objects.filter(pk=self.pk).update(hashed=self.hashed)

class LocBussiness(BaseModel):
    benefisiariu = models.ForeignKey( Benefisiariu,on_delete=models.CASCADE, verbose_name="Benefisiariu / Sira ne'ebé simu", related_name="locnegosiu")
    address = models.CharField(max_length=100, null=True, blank=True)
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, null=True)
    administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE, null=True, blank=True)
    village = models.ForeignKey(Village, on_delete=models.CASCADE, null=True, blank=True)
    aldeia = models.CharField(max_length=50, null=True, blank=True)
    latitude = models.CharField(max_length=20, null=True, blank=True)
    longitude = models.CharField(max_length=20, null=True, blank=True)
    area_polygon = models.TextField(blank=True, null=True)
    hashed = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.benefisiariu} - {self.municipality}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            LocBussiness.objects.filter(pk=self.pk).update(hashed=self.hashed)

class Program(BaseModel):
    benefisiariu = models.ForeignKey( Benefisiariu,on_delete=models.CASCADE, verbose_name="Benefisiariu / Sira ne'ebé simu", related_name="Pnegosiu")
    program_type = models.ForeignKey(TIpu_Programa, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Tipu Programa")
    t_apoiu = models.ForeignKey(Tipu_Apoio, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Tipu Apoiu")
    t_fundus = models.ForeignKey(Tipu_Fundus_Kapital, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Tipu Fundus Kapital")
    faze = models.ForeignKey(Faze,on_delete=models.CASCADE,null=True, blank=True, verbose_name="Faze (I, II, III)")
    year = models.ForeignKey(Year,on_delete=models.CASCADE,null=True, blank=True, verbose_name="Tinan")
    approved_amount = models.DecimalField(decimal_places=2,max_digits=10,verbose_name="Montante Aprova",null=True, blank=True)
    amount = models.DecimalField(decimal_places=2,max_digits=10,verbose_name="Montante Apoiu",null=True, blank=True)
    status = models.ForeignKey(Status,on_delete=models.CASCADE,null=True,verbose_name="Estadu", blank=True)
    hashed = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.benefisiariu} - {self.program_type}"

    def save(self, *args, **kwargs):
        if self.benefisiariu and self.benefisiariu.status:
            if self.benefisiariu.status.name == 'Parado':
                self.status = Status.objects.get(name='Parado')
            elif self.benefisiariu.status.name == 'Ativu':
                self.status = Status.objects.get(name='Ativu')
                
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            Program.objects.filter(pk=self.pk).update(hashed=self.hashed)


class Employee(BaseModel):
    business = models.ForeignKey(Business,on_delete=models.CASCADE,verbose_name="Negósiu")
    male = models.IntegerField(default=0, verbose_name="Mane")
    female = models.IntegerField(default=0, verbose_name="Feto")
    total = models.IntegerField(default=0, verbose_name="Total Trabalhador")
    hashed = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return str(self.business)

    def save(self, *args, **kwargs):
        self.total = (self.male or 0) + (self.female or 0)
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            Employee.objects.filter(pk=self.pk).update(hashed=self.hashed)


class Finance(BaseModel):
    business = models.ForeignKey(Business,on_delete=models.CASCADE,verbose_name="Negósiu")
    budget = models.FloatField(null=True, blank=True, verbose_name="Orsamentu Total")
    hashed = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return str(self.business)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            Finance.objects.filter(pk=self.pk).update(hashed=self.hashed)



class BusinessBaseline(BaseModel):
    business = models.OneToOneField( Business, on_delete=models.CASCADE, related_name='baseline', verbose_name="Negósiu")
    daily_income_before = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Rendimentu Loron Antes Apoiu ($)")
    monthly_income_before = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Rendimentu Fulan Antes Apoiu ($)")
    yearly_income_before = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Rendimentu Tinan Antes Apoiu ($)")
    employee_before = models.IntegerField(default=0, verbose_name="Total Trabalhador Antes Apoiu")
    asset_before = models.DecimalField(max_digits=12, decimal_places=2,  default=0, validators=[MinValueValidator(0)], verbose_name="Total Assets Antes Apoiu ($)")
    sales_before = models.DecimalField(max_digits=12, decimal_places=2,  default=0,  validators=[MinValueValidator(0)],verbose_name="Total Vendas Antes Apoiu ($)")
    note = models.TextField(null=True, blank=True, verbose_name="Observasaun")
    hashed = models.CharField(max_length=128,  null=True,   blank=True)

    def __str__(self):
        return f"{self.business} - Baseline"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(
                str(self.id).encode()
            ).hexdigest()
            BusinessBaseline.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        verbose_name = "Dadus Inisiál Negósiu"
        verbose_name_plural = "Dadus Inisiál Negósiu Sira"
        ordering = ['-id']

class BusinessMonitoring(BaseModel):
    STATUS_CHOICES = [
        ('Normal', 'Normal'),
        ('Risk', 'Risku'),
        ('Critical', 'Kritiku'),
        ('Inactive', 'La Ativu'),
    ]
    VERIFY_CHOICES = [
        ('Pending', 'Pending'),
        ('Verified', 'Verifikadu'),
        ('Rejected', 'Rejeitadu'),
    ]
    SOURCE_CHOICES = [
        ('Benefisiariu', 'Benefisiariu'),
        ('Officer', 'Officer'),
        ('Survey', 'Survey'),
    ]
    business = models.ForeignKey(Business,  on_delete=models.CASCADE, related_name='monitorings', verbose_name="Negósiu")
    year = models.ForeignKey(Year, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Tinan")
    month = models.CharField(max_length=20, null=True, blank=True, verbose_name="Fulan")
    monitoring_date = models.DateField(auto_now_add=True, verbose_name="Data Monitorizasaun")
    daily_income = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Rendimentu Loron ($)")
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Rendimentu Fulan ($)")
    yearly_income = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Rendimentu Tinan ($)")
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total Vendas ($)")
    total_assets = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total Assets ($)")
    total_employee = models.IntegerField(default=0, verbose_name="Total Trabalhador")
    growth_percentage = models.FloatField(default=0, verbose_name="Percentajen Cresimentu (%)")
    source_data = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='Benefisiariu', verbose_name="Fonte Dadus")
    verification_status = models.CharField(max_length=20, choices=VERIFY_CHOICES, default='Pending', verbose_name="Status Verifikasaun")
    monitoring_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Normal', verbose_name="Status Monitorizasaun")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='business_monitoring_user', verbose_name="Upload Husi")
    evidence_file = models.FileField(upload_to='monitoring/evidence/', null=True, blank=True, verbose_name="Dokumentu Evidensia")
    note = models.TextField(null=True, blank=True, verbose_name="Observasaun")
    hashed = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.business} - {self.month or ''} {self.year or ''}"

    def save(self, *args, **kwargs):
        try:
            baseline = self.business.baseline
        except BusinessBaseline.DoesNotExist:
            baseline = None
        if self.verification_status == 'Verified':
            if baseline and baseline.monthly_income_before:
                before = float(baseline.monthly_income_before)
                current = float(self.monthly_income or 0)
                if before > 0:
                    growth = ((current - before) / before) * 100
                    self.growth_percentage = round(growth, 2)
                    if growth < -50:
                        self.monitoring_status = 'Critical'
                    elif growth < 0:
                        self.monitoring_status = 'Risk'
                    else:
                        self.monitoring_status = 'Normal'
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(
                str(self.id).encode()
            ).hexdigest()

            BusinessMonitoring.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        verbose_name = "Monitorizasaun Negósiu"
        verbose_name_plural = "Monitorizasaun Negósiu Sira"
        ordering = ['-monitoring_date']