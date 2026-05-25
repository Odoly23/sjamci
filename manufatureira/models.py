import hashlib
from django.db import models
from django.contrib.auth.models import User
from custom.models import BaseModel, Municipality, AdministrativePost, Village, Status, IndustryType, Tipu_Apoio, Year
from benefisiariu.models import Benefisiariu
from kni.models import Business, Program 

class Manufatur(BaseModel):
    name         = models.CharField(max_length=200, verbose_name="Naran Manufatura")
    benefisiariu = models.ForeignKey(Benefisiariu, on_delete=models.CASCADE, null=True, blank=True, related_name="manufatur_set", verbose_name="Benefisiariu")
    business     = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True, related_name="manufatur_setes", verbose_name="Negosiu (se iha ona)", help_text="Opsionál — liga ba Business se benefisiariu ne'e registu iha KNI/KS/ADI")
    leader_name  = models.CharField(max_length=200, verbose_name="Naran Lider")
    phone        = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone")
    status       = models.CharField(max_length=50, null=True, blank=True, verbose_name="Estadu")
    hashed       = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            Manufatur.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        verbose_name        = "Manufatura"
        verbose_name_plural = "Manufatura Sira"
        ordering            = ["name"]


class Lokalizasaun(BaseModel):
    manufatur          = models.OneToOneField(Manufatur, on_delete=models.CASCADE, related_name='lokalidade', null=True, blank=True)
    municipality       = models.ForeignKey(Municipality,       on_delete=models.CASCADE, null=True)
    administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE, null=True)
    village            = models.ForeignKey(Village,            on_delete=models.CASCADE, null=True)
    aldeia             = models.CharField(max_length=50,  null=True, blank=True)
    latitude           = models.CharField(max_length=20,  null=True, blank=True)
    longitude          = models.CharField(max_length=20,  null=True, blank=True)
    area_polygon       = models.TextField(blank=True, null=True)
    hashed             = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.manufatur} - {self.aldeia}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            Lokalizasaun.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        verbose_name        = "Lokalizasaun"
        verbose_name_plural = "Lokalizasaun Sira"


class Membro(BaseModel):
    manufatur = models.OneToOneField(
        Manufatur, on_delete=models.CASCADE,
        related_name='members_data'
    )
    members = models.IntegerField(null=True, blank=True)
    male    = models.IntegerField(default=0)
    female  = models.IntegerField(default=0)
    hashed  = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.manufatur} - {self.members}"

    def save(self, *args, **kwargs):
        self.members = (self.male or 0) + (self.female or 0)
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            Membro.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        verbose_name        = "Membro"
        verbose_name_plural = "Membro Sira"


class Aktividade(BaseModel):
    manufatur    = models.ForeignKey(
        Manufatur, on_delete=models.CASCADE,
        related_name='atividades'
    )
    # ── Tambahan: link ke Program jika aktividade ini
    #    terkait dengan program KNI/KS/ADI yang sudah ada
    program      = models.ForeignKey(
        Program, on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="manufatur_atividades",
        verbose_name="Programa (se iha ona)",
        help_text="Opsionál — liga ba Program se registu hanesan iha sistema"
    )
    industry_type = models.ForeignKey(IndustryType, on_delete=models.CASCADE, null=True)
    support_type  = models.ForeignKey(Tipu_Apoio,   on_delete=models.CASCADE, null=True)
    year          = models.ForeignKey(Year,          on_delete=models.CASCADE, null=True)
    amount        = models.FloatField(null=True, blank=True)
    status        = models.ForeignKey(Status,        on_delete=models.CASCADE, null=True)
    hashed        = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.manufatur} - {self.year}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            Aktividade.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        verbose_name        = "Aktividade"
        verbose_name_plural = "Aktividade Sira"
        ordering            = ["-year"]