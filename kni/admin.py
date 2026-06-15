from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

from kni.models import Business, LocBussiness, Program, Employee, Finance, BusinessMonitoring, BusinessBaseline
from benefisiariu.models import Benefisiariu
from custom.models import (
    Status, Municipality, AdministrativePost, Village,
    Category_Emp, TIpu_Programa, Sector, Faze, Year, Tipu_Fundus_Kapital
)


# =========================
# Resources (Import/Export)
# =========================

class BusinessResource(resources.ModelResource):
    benefisiariu = fields.Field(
        column_name='benefisiariu',
        attribute='benefisiariu',
        widget=ForeignKeyWidget(Benefisiariu, field='name')
    )
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category_Emp, field='name')
    )
    sector = fields.Field(
        column_name='sector',
        attribute='sector',
        widget=ForeignKeyWidget(Sector, field='name')
    )

    class Meta:
        model = Business
        fields = ('id', 'benefisiariu', 'category', 'name', 'idea', 'sector','size','hashed')
        export_order = ('id', 'benefisiariu', 'category', 'name', 'idea', 'sector', 'size','hashed')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class LocBussinessResource(resources.ModelResource):
    benefisiariu = fields.Field(
        column_name='benefisiariu',
        attribute='benefisiariu',
        widget=ForeignKeyWidget(Benefisiariu, field='name')
    )
    municipality = fields.Field(
        column_name='municipality',
        attribute='municipality',
        widget=ForeignKeyWidget(Municipality, field='name')
    )
    administrativepost = fields.Field(
        column_name='administrativepost',
        attribute='administrativepost',
        widget=ForeignKeyWidget(AdministrativePost, field='name')
    )
    village = fields.Field(
        column_name='village',
        attribute='village',
        widget=ForeignKeyWidget(Village, field='name')
    )

    class Meta:
        model = LocBussiness
        fields = ('id', 'benefisiariu', 'municipality', 'administrativepost', 'village', 'aldeia', 'latitude', 'longitude', 'hashed')
        export_order = ('id', 'benefisiariu', 'municipality', 'administrativepost', 'village', 'aldeia', 'latitude', 'longitude', 'hashed')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class ProgramResource(resources.ModelResource):
    benefisiariu = fields.Field(
        column_name='benefisiariu',
        attribute='benefisiariu',
        widget=ForeignKeyWidget(Benefisiariu, field='name')
    )
    program_type = fields.Field(
        column_name='program_type',
        attribute='program_type',
        widget=ForeignKeyWidget(TIpu_Programa, field='name')
    )
    faze = fields.Field(
        column_name='faze',
        attribute='faze',
        widget=ForeignKeyWidget(Faze, field='name')
    )
    year = fields.Field(
        column_name='year',
        attribute='year',
        widget=ForeignKeyWidget(Year, field='year')
    )
    status = fields.Field(
        column_name='status',
        attribute='status',
        widget=ForeignKeyWidget(Status, field='name')
    )
    t_fundus = fields.Field(
        column_name='t_fundus',
        attribute='t_fundus',
        widget=ForeignKeyWidget(Tipu_Fundus_Kapital, field='name')
    )
    class Meta:
        model = Program
        fields = ('id', 'benefisiariu', 'program_type', 'faze', 'year', 'approved_amount', 'amount', 'status', 'hashed','t_fundus')
        export_order = ('id', 'benefisiariu', 'program_type', 'faze', 'year', 'approved_amount', 'amount', 'status', 'hashed')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class EmployeeResource(resources.ModelResource):
    business = fields.Field(
        column_name='business',
        attribute='business',
        widget=ForeignKeyWidget(Business, field='name')
    )

    class Meta:
        model = Employee
        fields = ('id', 'business', 'male', 'female', 'total', 'hashed')
        export_order = ('id', 'business', 'male', 'female', 'total', 'hashed')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class FinanceResource(resources.ModelResource):
    business = fields.Field(
        column_name='business',
        attribute='business',
        widget=ForeignKeyWidget(Business, field='name')
    )

    class Meta:
        model = Finance
        fields = ('id', 'business', 'budget', 'hashed')
        export_order = ('id', 'business', 'budget', 'hashed')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class BusinessBaselineResource(resources.ModelResource):
    business = fields.Field(
        column_name='business',
        attribute='business',
        widget=ForeignKeyWidget(Business, field='name')
    )

    class Meta:
        model = BusinessBaseline
        fields = (
            'id', 'business',
            'daily_income_before', 'monthly_income_before', 'yearly_income_before',
            'employee_before', 'asset_before', 'sales_before',
            'note', 'hashed'
        )
        export_order = (
            'id', 'business',
            'daily_income_before', 'monthly_income_before', 'yearly_income_before',
            'employee_before', 'asset_before', 'sales_before',
            'note', 'hashed'
        )
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


class BusinessMonitoringResource(resources.ModelResource):
    business = fields.Field(
        column_name='business',
        attribute='business',
        widget=ForeignKeyWidget(Business, field='name')
    )
    year = fields.Field(
        column_name='year',
        attribute='year',
        widget=ForeignKeyWidget(Year, field='year')
    )

    class Meta:
        model = BusinessMonitoring
        fields = (
            'id', 'business', 'year', 'month', 'monitoring_date',
            'daily_income', 'monthly_income', 'yearly_income',
            'total_sales', 'total_assets', 'total_employee',
            'growth_percentage', 'source_data',
            'verification_status', 'monitoring_status',
            'note', 'hashed'
        )
        export_order = (
            'id', 'business', 'year', 'month', 'monitoring_date',
            'daily_income', 'monthly_income', 'yearly_income',
            'total_sales', 'total_assets', 'total_employee',
            'growth_percentage', 'source_data',
            'verification_status', 'monitoring_status',
            'note', 'hashed'
        )
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = False
        use_bulk = False


# =========================
# Base Admin
# =========================
class BaseAdmin(ImportExportModelAdmin):
    list_per_page = 25
    ordering = ['-id']

    readonly_fields = (
        'created_at',
        'updated_at',
        'deleted_at',
        'hashed',
    )

    list_filter = ['created_at']


# =========================
# Employee Inline
# =========================
class EmployeeInline(admin.StackedInline):
    model = Employee
    extra = 0


# =========================
# Finance Inline
# =========================
class FinanceInline(admin.StackedInline):
    model = Finance
    extra = 0


# =========================
# Business
# =========================
@admin.register(Business)
class BusinessAdmin(BaseAdmin):
    resource_classes = [BusinessResource]

    list_display = (
        'id',
        'benefisiariu',
        'name',
        'idea',
        'sector',
        'category',
    )

    search_fields = (
        'name',
        'idea',
        'benefisiariu__name',
        'hashed',
    )

    list_filter = (
        'sector',
        'category',
    )

    inlines = [
        EmployeeInline,
        FinanceInline,
    ]

    fieldsets = (
        ('Informasaun Negósiu', {
            'fields': (
                'benefisiariu',
                'category',
                'name',
                'idea',
                'sector',
                'hashed',
            )
        }),

        ('System Information', {
            'classes': ('collapse',),
            'fields': (
                'created_by',
                'created_at',
                'updated_by',
                'updated_at',
                'deleted_by',
                'deleted_at',
            )
        }),
    )


# =========================
# Location Business
# =========================
@admin.register(LocBussiness)
class LocBussinessAdmin(BaseAdmin):
    resource_classes = [LocBussinessResource]

    list_display = (
        'id',
        'benefisiariu',
        'municipality',
        'administrativepost',
        'village',
    )

    search_fields = (
        'benefisiariu__name',
        'aldeia',
        'hashed',
    )

    list_filter = (
        'municipality',
        'administrativepost',
    )

    fieldsets = (
        ('Lokalizasaun Negósiu', {
            'fields': (
                'benefisiariu',
                'municipality',
                'administrativepost',
                'village',
                'aldeia',
                'latitude',
                'longitude',
                'area_polygon',
                'hashed',
            )
        }),

        ('System Information', {
            'classes': ('collapse',),
            'fields': (
                'created_by',
                'created_at',
                'updated_by',
                'updated_at',
                'deleted_by',
                'deleted_at',
            )
        }),
    )


# =========================
# Program
# =========================
@admin.register(Program)
class ProgramAdmin(BaseAdmin):
    resource_classes = [ProgramResource]

    list_display = (
        'id',
        'benefisiariu',
        'program_type',
        'faze',
        'year',
        'approved_amount',
        'amount',
        'status',
    )

    search_fields = (
        'benefisiariu__name',
        'hashed',
    )

    list_filter = (
        'program_type',
        'faze',
        'year',
        'status',
    )

    fieldsets = (
        ('Program Information', {
            'fields': (
                'benefisiariu',
                'program_type',
                'faze',
                'year',
                'approved_amount',
                'amount',
                'status',
                't_fundus',
                'hashed',
            )
        }),

        ('System Information', {
            'classes': ('collapse',),
            'fields': (
                'created_by',
                'created_at',
                'updated_by',
                'updated_at',
                'deleted_by',
                'deleted_at',
            )
        }),
    )


# =========================
# Employee
# =========================
@admin.register(Employee)
class EmployeeAdmin(BaseAdmin):
    resource_classes = [EmployeeResource]

    list_display = (
        'id',
        'business',
        'male',
        'female',
        'total',
    )

    search_fields = (
        'business__name',
        'hashed',
    )


# =========================
# Finance
# =========================
@admin.register(Finance)
class FinanceAdmin(BaseAdmin):
    resource_classes = [FinanceResource]

    list_display = (
        'id',
        'business',
        'budget',
    )

    search_fields = (
        'business__name',
        'hashed',
    )


# =========================
# Business Baseline
# =========================
@admin.register(BusinessBaseline)
class BusinessBaselineAdmin(BaseAdmin):
    resource_classes = [BusinessBaselineResource]

    list_display = (
        'id',
        'business',
        'daily_income_before',
        'monthly_income_before',
        'yearly_income_before',
        'employee_before',
        'asset_before',
        'sales_before',
    )

    search_fields = (
        'business__name',
        'hashed',
    )

    fieldsets = (
        ('Dadus Inisiál Negósiu', {
            'fields': (
                'business',
                'daily_income_before',
                'monthly_income_before',
                'yearly_income_before',
                'employee_before',
                'asset_before',
                'sales_before',
                'note',
                'hashed',
            )
        }),

        ('System Information', {
            'classes': ('collapse',),
            'fields': (
                'created_at',
                'updated_at',
                'deleted_at',
            )
        }),
    )


# =========================
# Business Monitoring
# =========================
@admin.register(BusinessMonitoring)
class BusinessMonitoringAdmin(BaseAdmin):
    resource_classes = [BusinessMonitoringResource]

    list_display = (
        'id',
        'business',
        'year',
        'month',
        'monitoring_date',
        'monthly_income',
        'growth_percentage',
        'monitoring_status',
        'verification_status',
    )

    search_fields = (
        'business__name',
        'hashed',
    )

    list_filter = (
        'year',
        'month',
        'monitoring_status',
        'verification_status',
        'source_data',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
        'deleted_at',
        'hashed',
        'monitoring_date',
        'growth_percentage',
        'monitoring_status',
    )

    fieldsets = (
        ('Monitorizasaun Negósiu', {
            'fields': (
                'business',
                'year',
                'month',
                'monitoring_date',
                'source_data',
                'verification_status',
            )
        }),

        ('Dadus Finanseiru', {
            'fields': (
                'daily_income',
                'monthly_income',
                'yearly_income',
                'total_sales',
                'total_assets',
                'total_employee',
            )
        }),

        ('Rezultadu Análize', {
            'fields': (
                'growth_percentage',
                'monitoring_status',
                'note',
                'evidence_file',
                'hashed',
            )
        }),

        ('System Information', {
            'classes': ('collapse',),
            'fields': (
                'created_at',
                'updated_at',
                'deleted_at',
            )
        }),
    )