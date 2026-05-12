import hashlib
from django.db import models
from django.core.validators import MinValueValidator
from benefisiariu.models import Benefisiariu
from kni.models import Business
from custom.models import BaseModel, Status, Municipality, AdministrativePost, Village, Category_Emp, TIpu_Programa, Sector, Faze, Year
from kni.models import Business

class EkipaMember(BaseModel):
    ROLE_CHOICES = [
        ("Xefi",    "Xefi Ekipa"),
        ("Tekniko", "Tekniko"),
    ]
    benefisiariu = models.ForeignKey(Benefisiariu, on_delete=models.CASCADE, related_name="team_members", verbose_name="Benefisiariu")
    name     = models.CharField(max_length=100, verbose_name="Naran")
    phone    = models.CharField(max_length=20, blank=True, null=True, verbose_name="Nu. Kontakto")
    role     = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name="Funsaun")
    is_active = models.BooleanField(default=True, verbose_name="Ativu?")
    hashed = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.role}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            EkipaMember.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        ordering     = ["name"]
        verbose_name = "Membru Ekipa"
        verbose_name_plural = "Membru Ekipa Sira"



class ProductService(BaseModel):
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="products",verbose_name="Negosiu")
    name                 = models.CharField(max_length=200, verbose_name="Tipu Produto/Servisu")
    production_volume    = models.CharField(max_length=100, blank=True, null=True, verbose_name="Volume Produsaun")
    production_frequency = models.CharField(max_length=100, blank=True, null=True, verbose_name="Frekuensia Produsaun")
    sales_volume         = models.CharField(max_length=100, blank=True, null=True, verbose_name="Volume Vendas")
    sales_frequency      = models.CharField(max_length=100, blank=True, null=True, verbose_name="Frekuensia Vendas")
    sales_amount         = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)], verbose_name="Montante Vendas ($)")
    hashed = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.sales_amount}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            ProductService.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        verbose_name        = "Produto/Servisu"
        verbose_name_plural = "Produto/Servisu Sira"



class MainCustomer(BaseModel):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="customers", verbose_name="Negosiu")
    name          = models.CharField(max_length=200, verbose_name="Kliente Prinsipal")
    demand_volume = models.CharField(max_length=100, blank=True, null=True, verbose_name="Volume Demanda")
    frequency     = models.CharField(max_length=100, blank=True, null=True, verbose_name="Frekuensia")
    hashed = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.frequency}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            MarketAssessment.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        verbose_name        = "Kliente Prinsipal"
        verbose_name_plural = "Kliente Prinsipal Sira"

class Competitor(BaseModel):
    business = models.ForeignKey(Business,  on_delete=models.CASCADE, related_name="competitors", verbose_name="Negosiu")
    name          = models.CharField(max_length=200, verbose_name="Kompetitor Prinsipal")
    demand_volume = models.CharField(max_length=100, blank=True, null=True, verbose_name="Volume Demanda")
    frequency     = models.CharField(max_length=100, blank=True, null=True, verbose_name="Frekuensia")
    hashed = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.business} - {self.frequency}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            Competitor.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        verbose_name        = "Kompetitor"
        verbose_name_plural = "Kompetitor Sira"



class MarketAssessment(BaseModel):    
    PRIORITY_CHOICES = [
        ("High",   "Prioridade A'as"),
        ("Medium", "Prioridade Mediu"),
        ("Low",    "Prioridade Ki'ik"),
    ]
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name="market_assessment", verbose_name="Negosiu")
    promotion_strategy   = models.TextField(blank=True, null=True, verbose_name="Estratejia Promosaun Produto")
    current_challenges   = models.TextField(blank=True, null=True, verbose_name="Difikuldade Prinsipal Durante Hala'o Negosiu")
    long_term_challenges = models.TextField(blank=True, null=True, verbose_name="Dezafio Ba Longu Prazu")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, blank=True, null=True, verbose_name="Prioridade Dezafio ba Suksesu Negosiu")
    response_strategy    = models.TextField(blank=True, null=True, verbose_name="Estratejia/Inisiativa Atu Responde Dezafiu")
    hashed = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.business} - {self.priority}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            MarketAssessment.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        verbose_name        = "Avaliasaun Merkadu"
        verbose_name_plural = "Avaliasaun Merkadu Sira"


class FinancialAssessment(BaseModel):
    ACCOUNTING_CHOICES = [
        ("Yes",    "Iha Ona"),
        ("No",     "Laiha"),
        ("NotYet", "Seidauk"),
    ]
    INVENTORY_CHOICES = [
        ("Manual",   "Manual (Spreadsheet/Livru)"),
        ("Software", "Uza Software Gestaun Inventariu Dedicado"),
        ("RFID",     "Uza Teknolojia Kodigu-bar/RFID"),
        ("Combined", "Kombinasaun Manual no Automatiku"),
        ("None",     "La Ativu Halo Monitorizasaun"),
    ]

    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name="financial_assessment", verbose_name="Negosiu")
    accounting_book   = models.CharField(max_length=10, choices=ACCOUNTING_CHOICES, blank=True, null=True, verbose_name="Aplika Livru Kontabilidade ka Relatoriu Finanseiru?")
    inventory_method  = models.CharField(max_length=20, choices=INVENTORY_CHOICES, blank=True, null=True, verbose_name="Monitorizasaun Rikusoin (Assets) ka Inventariu")
    inventory_frequency = models.CharField(max_length=100, blank=True, null=True, verbose_name="Q29b. Frekuensia Monitorizasaun")
    monthly_revenue   = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Rendimento Kada Fulan ($)")
    annual_revenue    = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Q31. Rendimento Kada Tinan ($)")
    projected_revenue = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Projeta Rendimento Ba Tinan Oin Mai ($)")
    pays_tax          = models.BooleanField(blank=True, null=True, verbose_name="Selu Ona Impostu (Taxa)?")
    monthly_tax       = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Montante Taxa Kada Fulan ($)")
    total_assets      = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Total Assets ($)")
    hashed = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.role}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            FinancialAssessment.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        verbose_name        = "Avaliasaun Finanseiru"
        verbose_name_plural = "Avaliasaun Finanseiru Sira"

class FixedAsset(BaseModel):
    financial = models.ForeignKey(FinancialAssessment, on_delete=models.CASCADE, related_name="assets", verbose_name="Avaliasaun Finanseiru")
    name  = models.CharField(max_length=200, verbose_name="Asset Fixu")
    value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)], verbose_name="Montante ($)")
    hashed = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - (${self.value})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            Competitor.objects.filter(pk=self.pk).update(hashed=self.hashed)


    class Meta:
        verbose_name        = "Asset Fixu"
        verbose_name_plural = "Asset Fixu Sira"


class CreditInfo(BaseModel):
    business   = models.OneToOneField(Business, on_delete=models.CASCADE, related_name="credit_info", verbose_name="Negosiu")
    took_credit = models.BooleanField(blank=True, null=True, verbose_name="Foti Tan Kreditu Depois de Kredit Suave?")
    provider    = models.CharField(max_length=200, blank=True, null=True, verbose_name="Se Mak Fo Kreditu?")
    amount      = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)], verbose_name="Montante Kreditu Hetan ($)")
    satisfied   = models.BooleanField(blank=True, null=True, verbose_name="Tuir Ita Nia Espetativa?")
    wants_more  = models.BooleanField(blank=True, null=True, verbose_name="Hakarak Asesu Ba Kreditu Iha Futuro?")
    preferred_institution = models.CharField(max_length=200, blank=True, null=True, verbose_name="Institusaun Finanseiru Preferida")
    reason_preference = models.TextField(blank=True, null=True, verbose_name="Tamba Sa?")
    hashed = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.business} - {self.provider}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.hashed:
            self.hashed = hashlib.blake2b(str(self.id).encode()).hexdigest()
            CreditInfo.objects.filter(pk=self.pk).update(hashed=self.hashed)

    class Meta:
        verbose_name        = "Informasaun Kreditu"
        verbose_name_plural = "Informasaun Kreditu Sira"
