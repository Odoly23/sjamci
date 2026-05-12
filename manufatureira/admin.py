from django.contrib import admin
from .models import (
    Manufatur,
    Lokalizasaun,
    Membro,
    Aktividade,
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
# Inline Lokalizasaun
# =========================
class LokalizasaunInline(admin.StackedInline):
    model = Lokalizasaun
    extra = 0


# =========================
# Inline Membro
# =========================
class MembroInline(admin.StackedInline):
    model = Membro
    extra = 0


# =========================
# Inline Aktividade
# =========================
class AktividadeInline(admin.TabularInline):
    model = Aktividade
    extra = 0


# =========================
# Manufatur
# =========================
@admin.register(Manufatur)
class ManufaturAdmin(BaseAdmin):

    list_display = (
        'id',
        'name',
        'benefisiariu',
        'leader_name',
        'phone',
        'status',
    )

    search_fields = (
        'name',
        'leader_name',
        'phone',
        'hashed',
    )

    list_filter = (
        'status',
    )

    inlines = [
        LokalizasaunInline,
        MembroInline,
        AktividadeInline,
    ]

    fieldsets = (
        ('Informasaun Manufatur', {
            'fields': (
                'name',
                'benefisiariu',
                'leader_name',
                'phone',
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
# Lokalizasaun
# =========================
@admin.register(Lokalizasaun)
class LokalizasaunAdmin(BaseAdmin):

    list_display = (
        'id',
        'manufatur',
        'municipality',
        'administrativepost',
        'village',
        'aldeia',
    )

    search_fields = (
        'manufatur__name',
        'aldeia',
        'hashed',
    )

    list_filter = (
        'municipality',
        'administrativepost',
    )

    fieldsets = (
        ('Lokalizasaun', {
            'fields': (
                'manufatur',
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
# Membro
# =========================
@admin.register(Membro)
class MembroAdmin(BaseAdmin):

    list_display = (
        'id',
        'manufatur',
        'members',
        'male',
        'female',
    )

    search_fields = (
        'manufatur__name',
        'hashed',
    )

    fieldsets = (
        ('Dadus Membru', {
            'fields': (
                'manufatur',
                'members',
                'male',
                'female',
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
# Aktividade
# =========================
@admin.register(Aktividade)
class AktividadeAdmin(BaseAdmin):

    list_display = (
        'id',
        'manufatur',
        'industry_type',
        'support_type',
        'year',
        'amount',
        'status',
    )

    search_fields = (
        'manufatur__name',
        'hashed',
    )

    list_filter = (
        'industry_type',
        'support_type',
        'year',
        'status',
    )

    fieldsets = (
        ('Dadus Atividade', {
            'fields': (
                'manufatur',
                'industry_type',
                'support_type',
                'year',
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