import uuid ,hashlib, datetime, io, csv
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from custom.models import BaseModel, Status, Municipality, AdministrativePost, Village, Position, Diresaun, Departamento, Gabinete

class Emp(BaseModel):
	name = models.CharField(max_length=100, null=True, blank=False, verbose_name='Naran')
	sexo = models.CharField(max_length=4, choices=[('Mane','Mane'),('Feto','Feto')], null=True, blank=False)
	phone = models.CharField(max_length=10, verbose_name="Nu. Telf.", null=True)

	def __str__(self):
		return self.name


class EmpDivision(models.Model):
	employee = models.OneToOneField(Emp, on_delete=models.CASCADE, related_name="employeedivision", verbose_name="Pessoal")
	gabinete = models.ForeignKey(Gabinete, on_delete=models.CASCADE, null=True, blank=True, related_name="employeedivision", verbose_name="Gabinete")
	dn = models.ForeignKey(Diresaun, on_delete=models.CASCADE, null=True, blank=True, related_name="employeedivision", verbose_name="Diresaun Geral")
	department = models.ForeignKey(Departamento, on_delete=models.CASCADE, null=True, blank=True, related_name="employeedivision", verbose_name="Departamento")

	def __str__(self):
		template = '{0.employee} - {0.department}'
		return template.format(self)

class EmpPosition(models.Model):
	employee = models.OneToOneField(Emp, on_delete=models.CASCADE, related_name="employeeposition", verbose_name="Pessoal")
	position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True, related_name="employeeposition", verbose_name="Pojisaun")
	
	def __str__(self):
		template = '{0.position}'
		return template.format(self)

class EmpUser(BaseModel):
	emp = models.OneToOneField(Emp, on_delete=models.CASCADE, null=True, related_name="empuser")
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		template = '{0.emp} - {0.user}'
		return template.format(self)

class EmpPhoto(models.Model):
    emp   = models.OneToOneField(Emp, on_delete=models.CASCADE, related_name='empphoto')
    image = models.ImageField(upload_to='emp/photos/', null=True, blank=True)

    def __str__(self):
        return f"Foto - {self.emp.name}"

    def get_photo_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/media/default.png'

class AuditLogin(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="audituserlogin")
	login_time = models.DateTimeField(auto_now_add=True,null=True,blank=True)
	logout_time  = models.DateTimeField(null=True, blank=True)
	duration     = models.DurationField(null=True, blank=True)        
	ip_address   = models.GenericIPAddressField(null=True, blank=True)
	user_agent   = models.TextField(null=True, blank=True)            
	is_active    = models.BooleanField(default=True)  

	def __str__(self):
		return f'{self.user} - {self.login_time}'
		