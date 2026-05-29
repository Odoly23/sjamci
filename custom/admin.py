from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

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
    Tipu_Fundus_Kapital
)


# =========================
# Resources (Import/Export)
# =========================

class MinisterResource(resources.ModelResource):
    class Meta:
        model = Minister
        fields = ('id', 'code', 'name', 'hashed')
        export_order = ('id', 'code', 'name', 'hashed')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class DiresaunResource(resources.ModelResource):
    class Meta:
        model = Diresaun
        fields = ('id', 'code', 'name')
        export_order = ('id', 'code', 'name')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class DepartamentoResource(resources.ModelResource):
    diresaun = fields.Field(
        column_name='diresaun',
        attribute='diresaun',
        widget=ForeignKeyWidget(Diresaun, field='name')
    )

    class Meta:
        model = Departamento
        fields = ('id', 'code', 'name', 'diresaun')
        export_order = ('id', 'code', 'name', 'diresaun')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class PositionResource(resources.ModelResource):
    class Meta:
        model = Position
        fields = ('id', 'name')
        export_order = ('id', 'name')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class GabineteResource(resources.ModelResource):
    class Meta:
        model = Gabinete
        fields = ('id', 'code', 'name', 'hashed')
        export_order = ('id', 'code', 'name', 'hashed')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class MunicipalityResource(resources.ModelResource):
    class Meta:
        model = Municipality
        fields = ('id', 'code', 'name', 'hckey')
        export_order = ('id', 'code', 'name', 'hckey')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class AdministrativePostResource(resources.ModelResource):
    municipality = fields.Field(
        column_name='municipality',
        attribute='municipality',
        widget=ForeignKeyWidget(Municipality, field='name')
    )

    class Meta:
        model = AdministrativePost
        fields = ('id', 'name', 'municipality')
        export_order = ('id', 'name', 'municipality')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class VillageResource(resources.ModelResource):
    administrativepost = fields.Field(
        column_name='administrativepost',
        attribute='administrativepost',
        widget=ForeignKeyWidget(AdministrativePost, field='name')
    )

    class Meta:
        model = Village
        fields = ('id', 'name', 'administrativepost')
        export_order = ('id', 'name', 'administrativepost')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class SectorResource(resources.ModelResource):
    class Meta:
        model = Sector
        fields = ('id', 'name')
        export_order = ('id', 'name')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class BussinesSizeResource(resources.ModelResource):
    class Meta:
        model = Bussines_size
        fields = ('id', 'code', 'name')
        export_order = ('id', 'code', 'name')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class StatusResource(resources.ModelResource):
    class Meta:
        model = Status
        fields = ('id', 'name')
        export_order = ('id', 'name')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class CategoryEmpResource(resources.ModelResource):
    class Meta:
        model = Category_Emp
        fields = ('id', 'name')
        export_order = ('id', 'name')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class YearResource(resources.ModelResource):
    class Meta:
        model = Year
        fields = ('id', 'year', 'is_active')
        export_order = ('id', 'year', 'is_active')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class FazeResource(resources.ModelResource):
    class Meta:
        model = Faze
        fields = ('id', 'name', 'is_active')
        export_order = ('id', 'name', 'is_active')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class TipuApoioResource(resources.ModelResource):
    class Meta:
        model = Tipu_Apoio
        fields = ('id', 'name')
        export_order = ('id', 'name')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class IndustryTypeResource(resources.ModelResource):
    class Meta:
        model = IndustryType
        fields = ('id', 'name')
        export_order = ('id', 'name')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class TipoProgramaResource(resources.ModelResource):
    class Meta:
        model = TIpu_Programa
        fields = ('id', 'name', 'is_active')
        export_order = ('id', 'name', 'is_active')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False

class Tipu_Fundus_KapitalResource(resources.ModelResource):
    class Meta:
        model = Tipu_Fundus_Kapital
        fields = ('id', 'name', 'is_active')
        export_order = ('id', 'name', 'is_active')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


# =========================
# Base Admin
# =========================
class BaseAdmin(ImportExportModelAdmin):
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
    resource_classes = [MinisterResource]
    list_display = ['id', 'code', 'name', 'hashed']
    search_fields = ['name', 'code']


# =========================
# Diresaun
# =========================
@admin.register(Diresaun)
class DiresaunAdmin(BaseAdmin):
    resource_classes = [DiresaunResource]
    list_display = ['id', 'code', 'name']
    search_fields = ['name', 'code']


# =========================
# Departamento
# =========================
@admin.register(Departamento)
class DepartamentoAdmin(BaseAdmin):
    resource_classes = [DepartamentoResource]
    list_display = ['id', 'code', 'name', 'diresaun']
    list_filter = ['diresaun']
    search_fields = ['name', 'code']


# =========================
# Position
# =========================
@admin.register(Position)
class PositionAdmin(BaseAdmin):
    resource_classes = [PositionResource]
    list_display = ['id', 'name']


# =========================
# Gabinete
# =========================
@admin.register(Gabinete)
class GabineteAdmin(ImportExportModelAdmin):
    resource_classes = [GabineteResource]
    list_display = ['id', 'code', 'name', 'hashed']
    search_fields = ['name', 'code']


# =========================
# Municipality
# =========================
@admin.register(Municipality)
class MunicipalityAdmin(BaseAdmin):
    resource_classes = [MunicipalityResource]
    list_display = ['id', 'code', 'name', 'hckey']
    search_fields = ['name', 'code']


# =========================
# AdministrativePost
# =========================
@admin.register(AdministrativePost)
class AdministrativePostAdmin(BaseAdmin):
    resource_classes = [AdministrativePostResource]
    list_display = ['id', 'name', 'municipality']
    list_filter = ['municipality']
    search_fields = ['name']


# =========================
# Village
# =========================
@admin.register(Village)
class VillageAdmin(BaseAdmin):
    resource_classes = [VillageResource]
    list_display = ['id', 'name', 'administrativepost']
    list_filter = ['administrativepost']
    search_fields = ['name']


# =========================
# Sector
# =========================
@admin.register(Sector)
class SectorAdmin(BaseAdmin):
    resource_classes = [SectorResource]
    list_display = ['id', 'name']


# =========================
# Bussines Size
# =========================
@admin.register(Bussines_size)
class BussinesSizeAdmin(BaseAdmin):
    resource_classes = [BussinesSizeResource]
    list_display = ['id', 'code', 'name']
    search_fields = ['name', 'code']


# =========================
# Status
# =========================
@admin.register(Status)
class StatusAdmin(BaseAdmin):
    resource_classes = [StatusResource]
    list_display = ['id', 'name']


# =========================
# Category Employee
# =========================
@admin.register(Category_Emp)
class CategoryEmpAdmin(BaseAdmin):
    resource_classes = [CategoryEmpResource]
    list_display = ['id', 'name']


# =========================
# Year
# =========================
@admin.register(Year)
class YearAdmin(ImportExportModelAdmin):
    resource_classes = [YearResource]
    list_display = ['id', 'year', 'is_active']
    list_filter = ['is_active']
    search_fields = ['year']


# =========================
# Faze
# =========================
@admin.register(Faze)
class FazeAdmin(ImportExportModelAdmin):
    resource_classes = [FazeResource]
    list_display = ['id', 'name', 'is_active']
    list_filter = ['is_active']


# =========================
# Tipu Apoio
# =========================
@admin.register(Tipu_Apoio)
class TipuApoioAdmin(BaseAdmin):
    resource_classes = [TipuApoioResource]
    list_display = ['id', 'name']


# =========================
# Industry Type
# =========================
@admin.register(IndustryType)
class IndustryTypeAdmin(BaseAdmin):
    resource_classes = [IndustryTypeResource]
    list_display = ['id', 'name']


# =========================
# Tipo Programa
# =========================
@admin.register(TIpu_Programa)
class TipoProgramaAdmin(ImportExportModelAdmin):
    resource_classes = [TipoProgramaResource]
    list_display = ['id', 'name', 'is_active']
    list_filter = ['is_active']


@admin.register(Tipu_Fundus_Kapital)
class Tipu_Fundus_KapitalAdmin(ImportExportModelAdmin):
    resource_classes = [Tipu_Fundus_KapitalResource]
    list_display = ['id', 'name', 'is_active']
    list_filter = ['is_active']