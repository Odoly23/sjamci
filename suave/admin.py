from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    EkipaMember,
    ProductService,
    MainCustomer,
    Competitor,
    MarketAssessment,
    FinancialAssessment,
    FixedAsset,
    CreditInfo,
)


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
# Fixed Asset Inline
# =========================
class FixedAssetInline(admin.TabularInline):
    model = FixedAsset
    extra = 0


# =========================
# Ekipa Member
# =========================
@admin.register(EkipaMember)
class EkipaMemberAdmin(BaseAdmin):

    list_display = (
        'id',
        'benefisiariu',
        'name',
        'role',
        'phone',
        'is_active',
    )

    search_fields = (
        'name',
        'phone',
        'benefisiariu__name',
        'hashed',
    )

    list_filter = (
        'role',
        'is_active',
    )


# =========================
# Product Service
# =========================
@admin.register(ProductService)
class ProductServiceAdmin(BaseAdmin):

    list_display = (
        'id',
        'business',
        'name',
        'sales_amount',
        'sales_frequency',
    )

    search_fields = (
        'name',
        'business__name',
        'hashed',
    )

    list_filter = (
        'sales_frequency',
    )


# =========================
# Main Customer
# =========================
@admin.register(MainCustomer)
class MainCustomerAdmin(BaseAdmin):

    list_display = (
        'id',
        'business',
        'name',
        'frequency',
    )

    search_fields = (
        'name',
        'business__name',
        'hashed',
    )


# =========================
# Competitor
# =========================
@admin.register(Competitor)
class CompetitorAdmin(BaseAdmin):

    list_display = (
        'id',
        'business',
        'name',
        'frequency',
    )

    search_fields = (
        'name',
        'business__name',
        'hashed',
    )


# =========================
# Market Assessment
# =========================
@admin.register(MarketAssessment)
class MarketAssessmentAdmin(BaseAdmin):

    list_display = (
        'id',
        'business',
        'priority',
    )

    search_fields = (
        'business__name',
        'hashed',
    )

    list_filter = (
        'priority',
    )

    fieldsets = (
        ('Avaliasaun Merkadu', {
            'fields': (
                'business',
                'promotion_strategy',
                'current_challenges',
                'long_term_challenges',
                'priority',
                'response_strategy',
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
# Financial Assessment
# =========================
@admin.register(FinancialAssessment)
class FinancialAssessmentAdmin(BaseAdmin):

    list_display = (
        'id',
        'business',
        'monthly_revenue',
        'annual_revenue',
        'total_assets',
    )

    search_fields = (
        'business__name',
        'hashed',
    )

    list_filter = (
        'accounting_book',
        'inventory_method',
        'pays_tax',
    )

    inlines = [
        FixedAssetInline,
    ]

    fieldsets = (
        ('Avaliasaun Finanseiru', {
            'fields': (
                'business',
                'accounting_book',
                'inventory_method',
                'inventory_frequency',
                'monthly_revenue',
                'annual_revenue',
                'projected_revenue',
                'pays_tax',
                'monthly_tax',
                'total_assets',
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
# Fixed Asset
# =========================
@admin.register(FixedAsset)
class FixedAssetAdmin(BaseAdmin):

    list_display = (
        'id',
        'financial',
        'name',
        'value',
    )

    search_fields = (
        'name',
        'financial__business__name',
        'hashed',
    )


# =========================
# Credit Info
# =========================
@admin.register(CreditInfo)
class CreditInfoAdmin(BaseAdmin):

    list_display = (
        'id',
        'business',
        'provider',
        'amount',
        'repayment_status',
    )

    search_fields = (
        'provider',
        'business__name',
        'hashed',
    )

    list_filter = (
        'repayment_status',
        'took_credit',
        'satisfied',
        'wants_more',
        'has_repayment_problem',
        'program_continuation',
    )

    fieldsets = (
        ('Informasaun Kreditu', {
            'fields': (
                'business',
                'took_credit',
                'provider',
                'amount',
                'satisfied',
                'wants_more',
                'preferred_institution',
                'reason_preference',
                'repayment_status',
                'repayment_notes',
                'recommendation',
                'collateral_amount',
                'approved_by_bank',
                'has_repayment_problem',
                'program_continuation',
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