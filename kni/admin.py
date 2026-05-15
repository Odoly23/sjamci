from django.contrib import admin
from kni.models import    Business, LocBussiness, Program, Employee, Finance

# =========================
# Base Admin
# =========================
class BaseAdmin(admin.ModelAdmin):
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

    list_display = (
        'id',
        'business',
        'budget',
    )

    search_fields = (
        'business__name',
        'hashed',
    )