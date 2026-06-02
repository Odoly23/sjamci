from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
    BusinessImpactMonitoring,
    FundUsage,
    BusinessAsset,
    CashFlow,
    FinancialBook,
)


# =====================================================
# RESOURCE
# =====================================================

class BusinessImpactMonitoringResource(resources.ModelResource):
    class Meta:
        model = BusinessImpactMonitoring


class FundUsageResource(resources.ModelResource):
    class Meta:
        model = FundUsage


class BusinessAssetResource(resources.ModelResource):
    class Meta:
        model = BusinessAsset


class CashFlowResource(resources.ModelResource):
    class Meta:
        model = CashFlow


class FinancialBookResource(resources.ModelResource):
    class Meta:
        model = FinancialBook


# =====================================================
# INLINE
# =====================================================

class FundUsageInline(admin.TabularInline):
    model = FundUsage
    extra = 0


class BusinessAssetInline(admin.TabularInline):
    model = BusinessAsset
    extra = 0


class CashFlowInline(admin.TabularInline):
    model = CashFlow
    extra = 0


class FinancialBookInline(admin.TabularInline):
    model = FinancialBook
    extra = 0


# =====================================================
# BUSINESS IMPACT MONITORING
# =====================================================

@admin.register(BusinessImpactMonitoring)
class BusinessImpactMonitoringAdmin(ImportExportModelAdmin):
    resource_class = BusinessImpactMonitoringResource

    list_display = (
        'business',
        'monitoring_date',
        'status',
        'fund_received',
        'fund_used',
        'fund_balance',
        'monthly_income',
        'monthly_expense',
        'monthly_profit',
        'total_employee',
        'created_at',
    )

    search_fields = (
        'business__name',
        'hashed',
        'observation',
    )

    list_filter = (
        'status',
        'use_accounting_book',
        'has_income',
        'paid_tax',
        'plan_credit',
        'plan_new_business',
        'monitoring_date',
        'created_at',
    )

    readonly_fields = (
        'fund_balance',
        'monthly_profit',
        'hashed',
        'created_at',
        'updated_at',
    )

    inlines = [
        FundUsageInline,
        BusinessAssetInline,
        CashFlowInline,
        FinancialBookInline,
    ]

    date_hierarchy = 'monitoring_date'

    list_per_page = 25


# =====================================================
# FUND USAGE
# =====================================================

@admin.register(FundUsage)
class FundUsageAdmin(ImportExportModelAdmin):
    resource_class = FundUsageResource

    list_display = (
        'monitoring',
        'item_name',
        'amount',
        'created_at',
    )

    search_fields = (
        'item_name',
        'description',
        'hashed',
        'monitoring__business__name',
    )

    readonly_fields = (
        'hashed',
        'created_at',
        'updated_at',
    )

    list_per_page = 25


# =====================================================
# BUSINESS ASSET
# =====================================================

@admin.register(BusinessAsset)
class BusinessAssetAdmin(ImportExportModelAdmin):
    resource_class = BusinessAssetResource

    list_display = (
        'asset_name',
        'monitoring',
        'quantity',
        'value',
        'condition',
        'created_at',
    )

    search_fields = (
        'asset_name',
        'hashed',
        'monitoring__business__name',
    )

    list_filter = (
        'condition',
        'created_at',
    )

    readonly_fields = (
        'hashed',
        'created_at',
        'updated_at',
    )

    list_per_page = 25


# =====================================================
# CASH FLOW
# =====================================================

@admin.register(CashFlow)
class CashFlowAdmin(ImportExportModelAdmin):
    resource_class = CashFlowResource

    list_display = (
        'transaction_date',
        'transaction_type',
        'description',
        'amount',
        'monitoring',
    )

    search_fields = (
        'description',
        'hashed',
        'monitoring__business__name',
    )

    list_filter = (
        'transaction_type',
        'transaction_date',
        'created_at',
    )

    readonly_fields = (
        'hashed',
        'created_at',
        'updated_at',
    )

    date_hierarchy = 'transaction_date'

    list_per_page = 25


# =====================================================
# FINANCIAL BOOK
# =====================================================

@admin.register(FinancialBook)
class FinancialBookAdmin(ImportExportModelAdmin):
    resource_class = FinancialBookResource

    list_display = (
        'title',
        'monitoring',
        'file',
        'created_at',
    )

    search_fields = (
        'title',
        'description',
        'hashed',
        'monitoring__business__name',
    )

    readonly_fields = (
        'hashed',
        'created_at',
        'updated_at',
    )

    list_per_page = 25
# Register your models here.
