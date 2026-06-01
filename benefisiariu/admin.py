from django.contrib import admin
from .models import   Benefisiariu,  AddressTL,   AddressOrigin,  Photo,  BeneficiariuEvaluation, BenefisiariuUser, Pedidu

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
    )

    list_filter = ['created_at']
    search_fields = ['id']


# =========================
# Address TL Inline
# =========================
class AddressTLInline(admin.StackedInline):
    model = AddressTL
    extra = 0


# =========================
# Address Origin Inline
# =========================
class AddressOriginInline(admin.StackedInline):
    model = AddressOrigin
    extra = 0


# =========================
# Photo Inline
# =========================
class PhotoInline(admin.StackedInline):
    model = Photo
    extra = 0


# =========================
# Benefisiariu
# =========================
@admin.register(Benefisiariu)
class BenefisiariuAdmin(BaseAdmin):
    list_display = (
        'id',
        'name',
        'sex',
        'phone',
        'status',
        'age',
    )

    search_fields = (
        'name',
        'phone',
        'hashed',
    )

    list_filter = (
        'sex',
        'marital',
        'status',
    )

    readonly_fields = BaseAdmin.readonly_fields + (
        'hashed',
    )

    inlines = [
        AddressTLInline,
        AddressOriginInline,
        PhotoInline,
    ]

    fieldsets = (
        ('Informasaun Benefisiariu', {
            'fields': (
                'name',
                'pob',
                'dob',
                'sex',
                'marital',
                'status',
                'phone',
                'file',
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
# Address TL
# =========================
@admin.register(AddressTL)
class AddressTLAdmin(BaseAdmin):
    list_display = (
        'id',
        'benefisiariu',
        'municipality',
        'administrativepost',
        'village',
    )

    list_filter = (
        'municipality',
        'administrativepost',
    )

    search_fields = (
        'benefisiariu__name',
        'address',
        'aldeia',
    )


# =========================
# Address Origin
# =========================
@admin.register(AddressOrigin)
class AddressOriginAdmin(BaseAdmin):
    list_display = (
        'id',
        'benefisiariu',
        'city',
        'address',
    )

    search_fields = (
        'benefisiariu__name',
        'city',
    )


# =========================
# Photo
# =========================
@admin.register(Photo)
class PhotoAdmin(BaseAdmin):
    list_display = (
        'id',
        'benefisiariu',
        'image',
    )

    search_fields = (
        'benefisiariu__name',
    )

@admin.register(BenefisiariuUser)
class BenefisiariuUserAdmin(admin.ModelAdmin): 
    list_display = ('id', 'benefisiariu', 'user')
    search_fields = ('benefisiariu__name', 'user__username')
    
@admin.register(Pedidu)
class PediduAdmin(BaseAdmin):
    list_display = ('id', 'benefisiariu', 'tipo', 'assuntu', 'status', 'created_at')
    list_filter = ('tipo', 'status', 'created_at')
    search_fields = ('benefisiariu__name', 'assuntu')
    readonly_fields = BaseAdmin.readonly_fields + ('hashed',)