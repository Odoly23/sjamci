import hashlib
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

#creates your models here.
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class BaseModel(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="%(class)s_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="%(class)s_updated")
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="%(class)s_deleted")
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = models.Manager()
    active_objects = ActiveManager()

    def soft_delete(self, user):
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()

    def restore(self):
        self.deleted_at = None
        self.deleted_by = None
        self.save()

    class Meta:
        abstract = True


class Minister(BaseModel):
	code = models.CharField(max_length=10, null=True, blank=True)
	name = models.CharField(max_length=50, verbose_name="Naran")
	hashed = models.CharField(max_length=128, null=True, blank=True)

	def __str__(self):
		template = '{0.name}'
		return template.format(self)

	def save(self, *args, **kwargs):
		self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
		return super(Minister, self).save(*args, **kwargs)


class Diresaun(BaseModel):
	code = models.CharField(max_length=10, null=True, blank=True)
	name = models.CharField(max_length=100, verbose_name="Naran")
	hashed = models.CharField(max_length=128, null=True, blank=True)

	def __str__(self):
		template = '{0.name}'
		return template.format(self)
	def save(self, *args, **kwargs):
		self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
		return super(Diresaun, self).save(*args, **kwargs)

class Departamento(BaseModel):
	code = models.CharField(max_length=10, null=True, blank=True)
	diresaun = models.ForeignKey(Diresaun, on_delete=models.CASCADE, null=True)
	name = models.CharField(max_length=100, verbose_name="Naran")
	hashed = models.CharField(max_length=128, null=True, blank=True)

	def __str__(self):
		template = '{0.name}'
		return template.format(self)
	def save(self, *args, **kwargs):
		self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
		return super(Departamento, self).save(*args, **kwargs)

class Position(BaseModel):
	name = models.CharField(max_length=100, verbose_name="Naran")
	def __str__(self):
		template = '{0.name}'
		return template.format(self)

class Gabinete(models.Model):
	code = models.CharField(max_length=10, null=True, blank=True)
	name = models.CharField(max_length=100, verbose_name="Naran")
	hashed = models.CharField(max_length=128, null=True, blank=True)

	def __str__(self):
		template = '{0.name}'
		return template.format(self)
	def save(self, *args, **kwargs):
		self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
		return super(Gabinete, self).save(*args, **kwargs)

class Municipality(BaseModel):
	code = models.CharField(max_length=5, null=True)
	name = models.CharField(max_length=100, verbose_name="Naran")
	hckey = models.CharField(max_length=10, null=True)

	def __str__(self):
		template = '{0.name}'
		return template.format(self)

class AdministrativePost(BaseModel):
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, null=True)
	name = models.CharField(max_length=100, verbose_name="Naran")
	def __str__(self):
		template = '{0.name}'
		return template.format(self)

class Village(BaseModel):
	administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE, null=True)
	name = models.CharField(max_length=100, verbose_name="Naran")
	def __str__(self):
		template = '{0.name}'
		return template.format(self)


class Sector(BaseModel):
	name = models.CharField(max_length=100, verbose_name="Naran")
	def __str__(self):
		template = '{0.name}'
		return template.format(self)

class Bussines_size(BaseModel):
	code = models.CharField(max_length=20, unique=True)
	name = models.CharField(max_length=100, verbose_name="Naran")
	
	def __str__(self):
		template = '{0.name}'
		return template.format(self)

class Status(BaseModel):
	name = models.CharField(max_length=100, verbose_name="Naran")
	def __str__(self):
		template = '{0.name}'
		return template.format(self)

class Category_Emp(BaseModel):
	name = models.CharField(max_length=100, verbose_name="Naran")
	def __str__(self):
		template = '{0.name}'
		return template.format(self)

class Year(BaseModel):
	year = models.IntegerField(null=True, blank=True)
	is_active = models.BooleanField(default=False)
	def __str__(self):
		template = '{0.year}'
		return template.format(self)

class Faze(BaseModel):
	name = models.CharField(max_length=10, null=True, blank=True)
	is_active = models.BooleanField(default=False)
	
	def __str__(self):
		template = '{0.name}'
		return template.format(self)

class Tipu_Apoio(BaseModel):
	name = models.CharField(max_length=100, verbose_name="Naran")
	def __str__(self):
		template = '{0.name}'
		return template.format(self)

class IndustryType(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class TIpu_Programa(BaseModel):
	name = models.CharField(max_length=20, null=True, blank=False)
	is_active = models.BooleanField(default=False)
	
	def __str__(self):
		template = '{0.name}'
		return template.format(self)

class TIPO_ATIVIDADE(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name