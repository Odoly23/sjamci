from django.contrib import admin
from django.utils.html import format_html
from .models import (
    mpmsEmpresa, mpmsLokalizasaun, mpmsLisensamentu, 
    mpmsKapital, mpmsEmpregador, mpmsMateriaPrima, mpmsAtividade
)
# Import TIPO_ATIVIDADE biar bisa register
from custom.models import TIPO_ATIVIDADE

# Register TIPO_ATIVIDADE dulu biar bisa dipake autocomplete
@admin.register(TIPO_ATIVIDADE)
class TipoAtividadeAdmin(admin.ModelAdmin):
    search_fields = ['name']  # Ganti 'name' sesuai field yang ada di TIPO_ATIVIDADE
    list_display = ['__str__']

class mpmsLokalizasaunInline(admin.StackedInline):
    model = mpmsLokalizasaun
    can_delete = False
    extra = 0
    fields = (
        'municipality', 'administrativepost', 'village', 'aldeia',
        ('latitude', 'longitude'),
        'rua_avenida', 'area_polygon'
    )

class mpmsLisensamentuInline(admin.StackedInline):
    model = mpmsLisensamentu
    can_delete = False
    extra = 0
    fields = ('lisensamentu', 'lisensamentu_status', 'tipo_rai')

class mpmsKapitalInline(admin.StackedInline):
    model = mpmsKapital
    can_delete = False
    extra = 0
    fields = (
        'kapital_investimento', 'tipu_fundus', 'total_fundus',
        ('lukru_brutu_mes', 'lukru_brutu_ano'),
        ('lukru_likidu_mes', 'lukru_likidu_ano'),
    )

class mpmsEmpregadorInline(admin.StackedInline):
    model = mpmsEmpregador
    can_delete = False
    extra = 0
    fields = (
        ('nasional_mane', 'nasional_feto'),
        ('internasional_mane', 'internasional_feto'),
        ('total_nasional', 'total_internasional', 'total_empregador'),
    )
    readonly_fields = ('total_nasional', 'total_internasional', 'total_empregador')

class mpmsMateriaPrimaInline(admin.StackedInline):
    model = mpmsMateriaPrima
    can_delete = False
    extra = 0
    fields = ('kustu', 'origem', 'deskrisaun')

class mpmsAtividadeInline(admin.TabularInline):
    model = mpmsAtividade
    extra = 0
    fields = ('program', 'tipu_apoio', 'year', 'amount', 'status', 'observasaun')
    autocomplete_fields = ['program', 'year', 'status']

@admin.register(mpmsEmpresa)
class mpmsEmpresaAdmin(admin.ModelAdmin):
    list_display = (
        'company_name', 'benefisiariu', 'tipo_atividade', 
        'tinan_hari', 'is_completed', 'get_total_empregador', 'hashed_short'
    )
    list_filter = (
        'is_completed', 'tipo_atividade', 'tinan_hari'
        # Hapus 'benefisiariu__municipality' karena error E116
    )
    search_fields = (
        'company_name', 'benefisiariu__name', 'hashed',
        'business__name'
    )
    autocomplete_fields = ['benefisiariu', 'business', 'tipo_atividade']
    readonly_fields = ('hashed',)
    list_editable = ('is_completed',)
    inlines = [
        mpmsLokalizasaunInline,
        mpmsLisensamentuInline,
        mpmsKapitalInline,
        mpmsEmpregadorInline,
        mpmsMateriaPrimaInline,
        mpmsAtividadeInline,
    ]
    fieldsets = (
        ('Dadus Baziku', {
            'fields': ('benefisiariu', 'business', 'company_name', 'tipo_atividade', 'tinan_hari')
        }),
        ('Status', {
            'fields': ('is_completed', 'hashed')
        }),
    )

    def get_total_empregador(self, obj):
        if hasattr(obj, 'empregador'):
            return obj.empregador.total_empregador
        return 0
    get_total_empregador.short_description = 'Total Empregador'

    def hashed_short(self, obj):
        if obj.hashed:
            return format_html('<code>{}</code>', obj.hashed[:16] + '...')
        return '-'
    hashed_short.short_description = 'Hash'

@admin.register(mpmsLokalizasaun)
class mpmsLokalizasaunAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'municipality', 'administrativepost', 'village', 'aldeia')
    list_filter = ('municipality', 'administrativepost')
    search_fields = ('empresa__company_name', 'aldeia', 'rua_avenida')
    autocomplete_fields = ['empresa', 'municipality', 'administrativepost', 'village']
    readonly_fields = ('hashed',)

@admin.register(mpmsLisensamentu)
class mpmsLisensamentuAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'lisensamentu', 'lisensamentu_status', 'tipo_rai')
    list_filter = ('lisensamentu', 'lisensamentu_status', 'tipo_rai')
    search_fields = ('empresa__company_name',)
    autocomplete_fields = ['empresa']
    readonly_fields = ('hashed',)

@admin.register(mpmsKapital)
class mpmsKapitalAdmin(admin.ModelAdmin):
    list_display = (
        'empresa', 'kapital_investimento', 'tipu_fundus', 
        'total_fundus', 'lukru_likidu_mes'
    )
    list_filter = ('kapital_investimento', 'tipu_fundus', 'total_fundus')
    search_fields = ('empresa__company_name',)
    autocomplete_fields = ['empresa']
    readonly_fields = ('hashed',)

@admin.register(mpmsEmpregador)
class mpmsEmpregadorAdmin(admin.ModelAdmin):
    list_display = (
        'empresa', 'total_nasional', 'total_internasional', 
        'total_empregador'
    )
    search_fields = ('empresa__company_name',)
    autocomplete_fields = ['empresa']
    readonly_fields = ('total_nasional', 'total_internasional', 'total_empregador', 'hashed')

@admin.register(mpmsMateriaPrima)
class mpmsMateriaPrimaAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'origem', 'kustu')
    list_filter = ('origem',)
    search_fields = ('empresa__company_name', 'deskrisaun')
    autocomplete_fields = ['empresa']
    readonly_fields = ('hashed',)

@admin.register(mpmsAtividade)
class mpmsAtividadeAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'tipu_apoio', 'program', 'year', 'amount', 'status')
    list_filter = ('tipu_apoio', 'year', 'status', 'program')
    search_fields = ('empresa__company_name', 'observasaun')
    autocomplete_fields = ['empresa', 'program', 'year', 'status']
    readonly_fields = ('hashed',)
    # Hapus date_hierarchy karena 'year' bukan DateField/DateTimeField