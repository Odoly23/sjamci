import hashlib
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from custom.models import BaseModel, Status, Municipality, AdministrativePost, Village, TIpu_Programa
from config.upload_utils import upload_estado, upload_photo


class Benefisiariu(BaseModel):
    name = models.CharField(max_length=100, null=True, verbose_name="Naran Empreza")
    pob = models.CharField(max_length=100, blank=True, null=True, verbose_name="Fatin Moris")
    dob = models.DateField(null=True, verbose_name="Data Moris")
    sex = models.CharField(choices=[('Mane', 'Mane'), ('Feto', 'Feto')],max_length=6, null=True, blank=True, verbose_name="Sexu")
    marital = models.CharField(choices=[('Solteiro/a', 'Solteiro/a'), ('Casado/a', 'Casado/a'), ('Divorciado/a', 'Divorciado/a'), ('Viuvo/a', 'Viuvo/a')], max_length=15, null=True, blank=True,verbose_name="Estado Civil")
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to=upload_estado, null=True, blank=True, validators=[FileExtensionValidator(['pdf'])], verbose_name="Anexa Eleitoral")
    phone = models.CharField(max_length=20, null=True, blank=True)
    hashed = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name 

    def age(self):
        if not self.dob:
            return None
        today = datetime.date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            super().save(update_fields=['hashed'])


class AddressTL(BaseModel):
    benefisiariu = models.OneToOneField(Benefisiariu, on_delete=models.CASCADE, related_name='addresstl')
    address = models.CharField(max_length=100, null=True, blank=True)
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, null=True)
    administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE, null=True)
    village = models.ForeignKey(Village, on_delete=models.CASCADE, null=True)
    aldeia = models.CharField(max_length=50, null=True, blank=True)

 

    def __str__(self):
        return f"{self.benefisiariu} - {self.address}"

class AddressOrigin(BaseModel):
    benefisiariu = models.OneToOneField(Benefisiariu, on_delete=models.CASCADE, related_name='addressorigin')
    city = models.CharField(max_length=50, null=True, blank=True, verbose_name="Sidade")
    address = models.CharField(max_length=100, null=True, blank=True, verbose_name="Hela Fatin")

    def __str__(self):
        return f"{self.benefisiariu} - {self.city}"

class Photo(BaseModel):
    benefisiariu = models.OneToOneField(Benefisiariu, on_delete=models.CASCADE, related_name='photo')
    image = models.ImageField(upload_to=upload_photo, default='default.png')

    def __str__(self):
        return str(self.benefisiariu)


class BeneficiariuEvaluation(BaseModel):
    STATUS_CHOICES = [
        ('Ativu', 'Ativu'),
        ('Parado', 'Parado'),
        ('Suspendu', 'Suspendu'),
        ('Pending', 'Pending'),
    ]
    benefisiariu = models.ForeignKey(Benefisiariu, on_delete=models.CASCADE, related_name='evaluations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Status")
    description = models.TextField(null=True, blank=True, verbose_name="Razaun")
    hashed = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return f"{self.benefisiariu} - {self.status}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            super().save(update_fields=['hashed'])
