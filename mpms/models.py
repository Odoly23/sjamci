import hashlib
from django.db import models
from django.core.validators import MinValueValidator
from benefisiariu.models import Benefisiariu
from kni.models import Business, Program
from custom.models import Municipality, AdministrativePost, Village, Year, Status, BaseModel, TIPO_ATIVIDADE


SEXO_CHOICES = [
    ('mane', 'Mane'),
    ('feto', 'Feto'),
]

NIVEL_EDUKASAUN_CHOICES = [
    ('primaria',       'Primária'),
    ('pre_secundaria', 'Pré-Secundária'),
    ('secundaria',     'Secundária'),
    ('lisensiatura',   'Lisensiatura'),
    ('mestrado',       'Mestrado'),
    ('doutoramento',   'Doutoramento'),
    ('seluk',          'Seluk'),
]

LISENSAMENTU_CHOICES = [
    ('iha',             'Iha'),
    ('laiha',           'Laiha'),
    ('sei_iha_prosesu', 'Sei iha Prosesu'),
]

LISENSAMENTU_STATUS_CHOICES = [
    ('valido',   'Válidu'),
    ('invalidu', 'Inválidu'),
]

TIPO_RAI_CHOICES = [
    ('rai_privado', 'Rai Privadu'),
    ('rai_aluguer', 'Rai Aluguer'),
    ('rai_estado',  'Rai Estadu'),
]

KAPITAL_RANGE_CHOICES = [
    ('0___5000',       '< $5,000'),
    ('5000___30_000',  '$5,000 – $30,000'),
    ('30_000___100_000', '$30,000 – $100,000'),
    ('100_000_acima',  '> $100,000'),
]

TIPU_FUNDUS_CHOICES = [
    ('home_industria__caseiras', 'Home Industria / Caseiras'),
    ('mikro',                    'Mikro'),
    ('pequenas',                 'Pequenas'),
    ('medias',                   'Médias'),
    ('grandes',                  'Grandes'),
]

TOTAL_FUNDUS_CHOICES = [
    ('1___5',   '1 – 5'),
    ('6___20',  '6 – 20'),
    ('21',      '21+'),
]

MATERIA_ORIGEM_CHOICES = [
    ('lokal',         'Lokal'),
    ('internasional', 'Internasionál'),
    ('kombinasaun',   'Kombinasaun'),
]

TIPU_APOIO_CHOICES = [
    ('treinamentu',    'Treinamentu'),
    ('ekipamentu',     'Ekipamentu'),
    ('finansiamentu',  'Finansiamentu'),
    ('konsultoria',    'Konsultória'),
    ('seluk',          'Seluk'),
]


class mpmsEmpresa(BaseModel):
    benefisiariu   = models.ForeignKey(Benefisiariu, on_delete=models.CASCADE, related_name='mpms_empresas', verbose_name='Benefisiariu')
    business       = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='mpms_empresas', verbose_name='Negosiu (se iha ona)',help_text='Opsionál — liga ba Business se benefisiariu ne\'e iha ona iha KNI/KS')
    company_name   = models.CharField(max_length=200, verbose_name='Naran Kompania')
    tipo_atividade = models.ForeignKey(TIPO_ATIVIDADE, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Tipo Atividade')
    tinan_hari     = models.CharField(max_length=4, null=True, blank=True, verbose_name='Tinan Hari Kompania')
    hashed         = models.CharField(max_length=128, null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.company_name} - {self.benefisiariu}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            mpmsEmpresa.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        verbose_name        = 'Empresa mpms'
        verbose_name_plural = 'Empresa mpms Sira'
        ordering            = ['company_name']

class mpmsLokalizasaun(BaseModel):
    empresa            = models.OneToOneField(mpmsEmpresa, on_delete=models.CASCADE,related_name='lokalizasaun', verbose_name='Empresa')
    municipality       = models.ForeignKey(Municipality,       on_delete=models.SET_NULL, null=True, verbose_name='Munisipiu')
    administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Postu Administrativu')
    village            = models.ForeignKey(Village,            on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Suku')
    aldeia             = models.CharField(max_length=100, null=True, blank=True, verbose_name='Aldeia')
    rua_avenida        = models.CharField(max_length=200, null=True, blank=True, verbose_name='Rua / Avenida')
    latitude           = models.CharField(max_length=20,  null=True, blank=True, verbose_name='Latitude')
    longitude          = models.CharField(max_length=20,  null=True, blank=True, verbose_name='Longitude')
    area_polygon       = models.TextField(null=True, blank=True)
    hashed             = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.empresa} - {self.municipality}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            mpmsLokalizasaun.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        verbose_name        = 'Lokalizasaun mpms'
        verbose_name_plural = 'Lokalizasaun mpms Sira'


class mpmsLisensamentu(BaseModel):
    empresa              = models.OneToOneField(mpmsEmpresa, on_delete=models.CASCADE, related_name='lisensamentu', verbose_name='Empresa'    )
    lisensamentu         = models.CharField(max_length=20, choices=LISENSAMENTU_CHOICES,  null=True, blank=True, verbose_name='Lisensamentu Atividade')
    lisensamentu_status  = models.CharField(max_length=10, choices=LISENSAMENTU_STATUS_CHOICES, null=True, blank=True, verbose_name='Lisensamentu Atividade Iha')
    tipo_rai             = models.CharField(max_length=20, choices=TIPO_RAI_CHOICES, null=True, blank=True, verbose_name='Tipo Propriodade / Rai Halao Atividade')
    hashed               = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.empresa} - {self.lisensamentu}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            mpmsLisensamentu.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        verbose_name        = 'Lisensamentu mpms'
        verbose_name_plural = 'Lisensamentu mpms Sira'



class mpmsKapital(BaseModel):
    empresa           = models.OneToOneField(mpmsEmpresa, on_delete=models.CASCADE,  related_name='kapital', verbose_name='Empresa')
    kapital_investimento = models.CharField(max_length=20, choices=KAPITAL_RANGE_CHOICES, null=True, blank=True, verbose_name='Kapital Investimento')
    tipu_fundus       = models.CharField(max_length=30, choices=TIPU_FUNDUS_CHOICES,  null=True, blank=True, verbose_name='Tipu Fundus Kapital')
    total_fundus      = models.CharField(max_length=10, choices=TOTAL_FUNDUS_CHOICES,   null=True, blank=True, verbose_name='Total Fundus')
    lukru_brutu_mes   = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='Total Lukru Brutu (Kotor) / Mes ($)')
    lukru_brutu_ano   = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='Total Lukru Brutu (Kotor) / Ano ($)')
    lukru_likidu_mes  = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='Lukru Likidu (Bersih) / Mes ($)')
    lukru_likidu_ano  = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='Lukru Likidu (Bersih) / Ano ($)')
    hashed            = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.empresa} - {self.tipu_fundus}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            mpmsKapital.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        verbose_name        = 'Kapital mpms'
        verbose_name_plural = 'Kapital mpms Sira'



class mpmsEmpregador(BaseModel):
    empresa              = models.OneToOneField(mpmsEmpresa, on_delete=models.CASCADE, related_name='empregador', verbose_name='Empresa')
    nasional_mane        = models.IntegerField(default=0, verbose_name='Nasionál Mane')
    nasional_feto        = models.IntegerField(default=0, verbose_name='Nasionál Feto')
    internasional_mane   = models.IntegerField(default=0, verbose_name='Internasionál Mane')
    internasional_feto   = models.IntegerField(default=0, verbose_name='Internasionál Feto')
    total_nasional       = models.IntegerField(default=0, verbose_name='Total Nasionál')
    total_internasional  = models.IntegerField(default=0, verbose_name='Total Internasionál')
    total_empregador     = models.IntegerField(default=0, verbose_name='Total Empregador')
    hashed               = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.empresa} - Total: {self.total_empregador}"

    def save(self, *args, **kwargs):
        # Auto hitung total
        self.total_nasional      = (self.nasional_mane or 0) + (self.nasional_feto or 0)
        self.total_internasional = (self.internasional_mane or 0) + (self.internasional_feto or 0)
        self.total_empregador    = self.total_nasional + self.total_internasional
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            mpmsEmpregador.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        verbose_name        = 'Empregador mpms'
        verbose_name_plural = 'Empregador mpms Sira'



class mpmsMateriaPrima(BaseModel):
    empresa       = models.OneToOneField(mpmsEmpresa, on_delete=models.CASCADE, related_name='materia_prima', verbose_name='Empresa')
    kustu         = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)],  verbose_name='Kustu ($) ba Materia Prima')
    origem        = models.CharField(max_length=20, choices=MATERIA_ORIGEM_CHOICES, null=True, blank=True, verbose_name="Materia Prima mai husi ne'ebe")
    deskrisaun    = models.TextField(null=True, blank=True, verbose_name='Deskrisaun Materia Prima')
    hashed        = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.empresa} - {self.origem}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            mpmsMateriaPrima.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        verbose_name        = 'Materia Prima mpms'
        verbose_name_plural = 'Materia Prima mpms Sira'



class mpmsAtividade(BaseModel):
    empresa      = models.ForeignKey(mpmsEmpresa, on_delete=models.CASCADE, related_name='atividades', verbose_name='Empresa')
    program      = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True, blank=True, related_name='mpms_atividades',  verbose_name='Programa (se iha ona)',
        help_text='Opsionál Karik Presija' )
    tipu_apoio   = models.CharField(max_length=20, choices=TIPU_APOIO_CHOICES, null=True, blank=True, verbose_name='Tipu Apoio')
    year         = models.ForeignKey(Year, on_delete=models.SET_NULL, null=True, verbose_name='Tinan')
    amount       = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)],     verbose_name='Montante Apoio ($)'
    )
    status       = models.ForeignKey(Status, on_delete=models.SET_NULL,  null=True, verbose_name='Estadu')
    observasaun  = models.TextField(null=True, blank=True, verbose_name='Observasaun')
    hashed       = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.empresa} - {self.tipu_apoio} ({self.year})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            mpmsAtividade.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        verbose_name        = 'Atividade mpms'
        verbose_name_plural = 'Atividade mpms Sira'
        ordering            = ['-year']
