from django.contrib import admin

from .models import OfflineSubmission


@admin.register(OfflineSubmission)
class OfflineSubmissionAdmin(admin.ModelAdmin):
    list_display = ('synced_at', 'user', 'module', 'benefisiariu', 'filled_at')
    list_filter = ('module', 'synced_at')
    search_fields = ('user__username', 'benefisiariu__name')
    readonly_fields = ('uuid', 'user', 'module', 'benefisiariu', 'filled_at', 'synced_at')

    def has_add_permission(self, request):
        return False
