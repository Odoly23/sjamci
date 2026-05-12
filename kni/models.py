import hashlib
from django.db import models
from benefisiariu.models import Benefisiariu
from django.utils import timezone
from custom.models import BaseModel, Status, Municipality, AdministrativePost, Village, Bussines_size, Category_Emp, TIpu_Programa, Sector, Faze,\
							Year
from config.upload_utils import upload_estado, upload_photo


class Business(BaseModel):
    benefisiariu = models.ForeignKey( Benefisiariu,on_delete=models.CASCADE, verbose_name="Benefisiariu / Sira ne'ebé simu", related_name="negosiu")
    category = models.ForeignKey(Category_Emp, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100,verbose_name="Naran Negósiu")
    idea = models.CharField(max_length=100,verbose_name="Ideia Negósiu", null=True, blank=True)
    sector = models.ForeignKey(Sector,on_delete=models.CASCADE,null=True, verbose_name="Sector Prinsipal")
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
            LocBusiness.objects.filter(pk=self.pk).update(hashed=self.hashed)

class Program(BaseModel):
    benefisiariu = models.ForeignKey( Benefisiariu,on_delete=models.CASCADE, verbose_name="Benefisiariu / Sira ne'ebé simu", related_name="Pnegosiu")
    program_type = models.ForeignKey(TIpu_Programa, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Tipu Apoiu")
    faze = models.ForeignKey(Faze,on_delete=models.CASCADE,null=True,verbose_name="Faze (I, II, III)")
    year = models.ForeignKey(Year,on_delete=models.CASCADE,null=True,verbose_name="Tinan")
    approved_amount = models.DecimalField(decimal_places=2,max_digits=10,verbose_name="Montante Aprova",null=True)
    amount = models.DecimalField(decimal_places=2,max_digits=10,verbose_name="Montante Apoiu",null=True)
    status = models.ForeignKey(Status,on_delete=models.CASCADE,null=True,verbose_name="Estadu")
    hashed = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.business.name} - {self.program_type}"

    def save(self, *args, **kwargs):
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


