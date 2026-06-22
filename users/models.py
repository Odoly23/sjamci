import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from custom.models import BaseModel, Position, Diresaun, Departamento, Gabinete

class Emp(BaseModel):
    name = models.CharField(max_length=100, verbose_name='Naran', null=True)
    sexo = models.CharField(max_length=4, null=True, choices=[('Mane','Mane'),('Feto','Feto')])
    phone = models.CharField(max_length=15, verbose_name="Nu. Telf.", validators=[RegexValidator(r'^\+?670\d{7,8}$', 'Format: +6707xxxxxxx')], null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    def __str__(self):
        return self.name

class EmpDivision(models.Model):
    employee = models.ForeignKey(Emp, on_delete=models.CASCADE, related_name="divisions")
    gabinete = models.ForeignKey(Gabinete, on_delete=models.CASCADE, null=True, blank=True)
    dn = models.ForeignKey(Diresaun, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Departamento, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        unit = self.department or self.dn or self.gabinete or 'Sem Unidade'
        return f'{self.employee.name} - {unit}'

class EmpPosition(models.Model):
    employee = models.ForeignKey(Emp, on_delete=models.CASCADE, related_name="positions")
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.employee.name} - {self.position}'

class EmpUser(BaseModel):
    emp = models.OneToOneField(Emp, on_delete=models.CASCADE, related_name="account", null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.emp.name} - {self.user.username}'

class EmpPhoto(models.Model):
    emp = models.OneToOneField(Emp, on_delete=models.CASCADE, related_name='photo')
    image = models.ImageField(upload_to='emp/photos/', null=True, blank=True)

    def __str__(self):
        return f"Foto - {self.emp.name}"

    @property
    def photo_url(self):
        if self.image:
            return self.image.url
        return '/static/img/default.png'

class AuditLogin(models.Model):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('funcionario', 'Funcionario'),
        ('chefe', 'Chefe'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="audit_logins")
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, null=True, blank=True)
    login_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)        
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)            
    is_active = models.BooleanField(default=True)  

    def save(self, *args, **kwargs):
        if self.logout_time and self.login_time:
            self.duration = self.logout_time - self.login_time
            self.is_active = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} - {self.login_time.strftime("%d/%m/%Y %H:%M")}'