from django.contrib import admin


class BaseAdmin(admin.ModelAdmin):
    """Base admin komun ba modelu sira ne'ebé herda BaseModel."""
    list_per_page = 25
    ordering = ['-id']

    readonly_fields = (
        'created_at',
        'updated_at',
        'deleted_at',
        'hashed',
    )

    list_filter = ['created_at']
