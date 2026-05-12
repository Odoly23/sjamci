from django.contrib import admin
from .models import (
    Minister,
    Diresaun,
    Departamento,
    Position,
    Gabinete,
    Municipality,
    AdministrativePost,
    Village,
    Sector,
    Bussines_size,
    Status,
    Category_Emp,
    Year,
    Faze,
    Tipu_Apoio,
    IndustryType,
    TIpu_Programa,
)


# =========================
# Base Admin
# =========================
class BaseAdmin(admin.ModelAdmin):
    list_per_page = 25
    ordering = ['id']
    readonly_fields = (
        'created_at',
        'updated_at',
        'deleted_at',
    )

    search_fields = ['name']

    list_filter = ['created_at']



# =========================
# Minister
# =========================
@admin.register(Minister)
class MinisterAdmin(BaseAdmin):
    list_display = ['id', 'code', 'name', 'hashed']
    search_fields = ['name', 'code']


# =========================
# Diresaun
# =========================
@admin.register(Diresaun)
class DiresaunAdmin(BaseAdmin):
    list_display = ['id', 'code', 'name']
    search_fields = ['name', 'code']


# =========================
# Departamento
# =========================
@admin.register(Departamento)
class DepartamentoAdmin(BaseAdmin):
    list_display = ['id', 'code', 'name', 'diresaun']
    list_filter = ['diresaun']
    search_fields = ['name', 'code']


# =========================
# Position
# =========================
@admin.register(Position)
class PositionAdmin(BaseAdmin):
    list_display = ['id', 'name']


# =========================
# Gabinete
# =========================
@admin.register(Gabinete)
class GabineteAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'hashed']
    search_fields = ['name', 'code']


# =========================
# Municipality
# =========================
@admin.register(Municipality)
class MunicipalityAdmin(BaseAdmin):
    list_display = ['id', 'code', 'name', 'hckey']
    search_fields = ['name', 'code']


# =========================
# AdministrativePost
# =========================
@admin.register(AdministrativePost)
class AdministrativePostAdmin(BaseAdmin):
    list_display = ['id', 'name', 'municipality']
    list_filter = ['municipality']
    search_fields = ['name']


# =========================
# Village
# =========================
@admin.register(Village)
class VillageAdmin(BaseAdmin):
    list_display = ['id', 'name', 'administrativepost']
    list_filter = ['administrativepost']
    search_fields = ['name']


# =========================
# Sector
# =========================
@admin.register(Sector)
class SectorAdmin(BaseAdmin):
    list_display = ['id', 'name']


# =========================
# Bussines Size
# =========================
@admin.register(Bussines_size)
class BussinesSizeAdmin(BaseAdmin):
    list_display = ['id', 'code', 'name']
    search_fields = ['name', 'code']


# =========================
# Status
# =========================
@admin.register(Status)
class StatusAdmin(BaseAdmin):
    list_display = ['id', 'name']


# =========================
# Category Employee
# =========================
@admin.register(Category_Emp)
class CategoryEmpAdmin(BaseAdmin):
    list_display = ['id', 'name']


# =========================
# Year
# =========================
@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ['id', 'year', 'is_active']
    list_filter = ['is_active']
    search_fields = ['year']


# =========================
# Faze
# =========================
@admin.register(Faze)
class FazeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active']
    list_filter = ['is_active']


# =========================
# Tipu Apoio
# =========================
@admin.register(Tipu_Apoio)
class TipuApoioAdmin(BaseAdmin):
    list_display = ['id', 'name']


# =========================
# Industry Type
# =========================
@admin.register(IndustryType)
class IndustryTypeAdmin(BaseAdmin):
    list_display = ['id', 'name']


# =========================
# Tipo Programa
# =========================
@admin.register(TIpu_Programa)
class TipoProgramaAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active']
    list_filter = ['is_active']