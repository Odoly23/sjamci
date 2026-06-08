from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'sender',
        'receiver',
        'notif_type',
        'is_read',
        'created_at',
    )

    list_filter = (
        'notif_type',
        'is_read',
        'created_at',
    )

    search_fields = (
        'title',
        'message',
        'sender__username',
        'receiver__username',
    )

    list_editable = (
        'is_read',
    )

    ordering = ('-created_at',)

    autocomplete_fields = ('sender', 'receiver')

    readonly_fields = ('created_at', 'updated_at')  # kalau BaseModel punya ini