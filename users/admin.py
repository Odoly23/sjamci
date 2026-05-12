from django.contrib import admin
from .models import (
    Emp,
    EmpDivision,
    EmpPosition,
    EmpUser,
    EmpPhoto,
    AuditLogin,
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
    )

    list_filter = ['created_at']


# =========================
# Inline Division
# =========================
class EmpDivisionInline(admin.StackedInline):
    model = EmpDivision
    extra = 0


# =========================
# Inline Position
# =========================
class EmpPositionInline(admin.StackedInline):
    model = EmpPosition
    extra = 0


# =========================
# Inline User
# =========================
class EmpUserInline(admin.StackedInline):
    model = EmpUser
    extra = 0


# =========================
# Inline Photo
# =========================
class EmpPhotoInline(admin.StackedInline):
    model = EmpPhoto
    extra = 0


# =========================
# Employee
# =========================
@admin.register(Emp)
class EmpAdmin(BaseAdmin):

    list_display = (
        'id',
        'name',
        'sexo',
        'phone',
    )

    search_fields = (
        'name',
        'phone',
    )

    list_filter = (
        'sexo',
    )

    inlines = [
        EmpDivisionInline,
        EmpPositionInline,
        EmpUserInline,
        EmpPhotoInline,
    ]

    fieldsets = (
        ('Dadus Pessoal', {
            'fields': (
                'name',
                'sexo',
                'phone',
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
# Employee Division
# =========================
@admin.register(EmpDivision)
class EmpDivisionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'employee',
        'gabinete',
        'dn',
        'department',
    )

    search_fields = (
        'employee__name',
    )

    list_filter = (
        'gabinete',
        'dn',
        'department',
    )


# =========================
# Employee Position
# =========================
@admin.register(EmpPosition)
class EmpPositionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'employee',
        'position',
    )

    search_fields = (
        'employee__name',
    )

    list_filter = (
        'position',
    )


# =========================
# Employee User
# =========================
@admin.register(EmpUser)
class EmpUserAdmin(BaseAdmin):

    list_display = (
        'id',
        'emp',
        'user',
    )

    search_fields = (
        'emp__name',
        'user__username',
    )


# =========================
# Employee Photo
# =========================
@admin.register(EmpPhoto)
class EmpPhotoAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'emp',
        'image',
    )

    search_fields = (
        'emp__name',
    )


# =========================
# Audit Login
# =========================
@admin.register(AuditLogin)
class AuditLoginAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'login_time',
    )

    search_fields = (
        'user__username',
    )

    readonly_fields = (
        'id',
        'user',
        'login_time',
    )

    ordering = ['-login_time']