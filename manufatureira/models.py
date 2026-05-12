import hashlib
from django.db import models
from django.contrib.auth.models import User
from custom.models import BaseModel, Municipality, AdministrativePost, Village, Status, IndustryType, Tipu_Apoio, Year
from benefisiariu.models import Benefisiariu

class Manufatur(BaseModel):
    name = models.CharField(max_length=200)
    benefisiariu = models.ForeignKey(Benefisiariu, on_delete=models.CASCADE, null=True, blank=True, related_name="manufatur_set")
    leader_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    hashed = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            Manufatur.objects.filter(pk=self.pk).update(hashed=self.hashed)


class Lokalizasaun(BaseModel):
    manufatur = models.OneToOneField(Manufatur, on_delete=models.CASCADE, related_name='lokalidade')
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, null=True)
    administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE, null=True)
    village = models.ForeignKey(Village, on_delete=models.CASCADE, null=True)
    aldeia = models.CharField(max_length=50, null=True, blank=True)
    latitude = models.CharField(max_length=20, null=True, blank=True)
    longitude = models.CharField(max_length=20, null=True, blank=True)
    area_polygon = models.TextField(blank=True, null=True)
    hashed = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.manufatur} - {self.aldeia}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            Lokalizasaun.objects.filter(pk=self.pk).update(hashed=self.hashed)


class Membro(BaseModel):
    manufatur = models.OneToOneField(Manufatur, on_delete=models.CASCADE, related_name='members_data')
    members = models.IntegerField(null=True, blank=True)
    male = models.IntegerField(default=0)
    female = models.IntegerField(default=0)
    hashed = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.manufatur} - {self.members}"

    def save(self, *args, **kwargs):
        self.members = (self.male or 0) + (self.female or 0)
        super().save(*args, **kwargs)

        if not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            Membro.objects.filter(pk=self.pk).update(hashed=self.hashed)


class Aktividade(BaseModel):
    manufatur = models.ForeignKey(Manufatur, on_delete=models.CASCADE, related_name='atividades')
    industry_type = models.ForeignKey(IndustryType, on_delete=models.SET_NULL, null=True)
    support_type = models.ForeignKey(Tipu_Apoio, on_delete=models.SET_NULL, null=True)
    year = models.ForeignKey(Year, on_delete=models.SET_NULL, null=True)
    amount = models.FloatField(null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True)
    hashed = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.manufatur} - {self.year}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            Aktividade.objects.filter(pk=self.pk).update(hashed=self.hashed)