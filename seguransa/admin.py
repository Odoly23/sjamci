from django.contrib import admin

from .models import ActivityLog, UserSecurity


@admin.register(UserSecurity)
class UserSecurityAdmin(admin.ModelAdmin):
    list_display = ('user', 'must_change_password', 'totp_enabled', 'password_changed_at')
    list_filter = ('must_change_password', 'totp_enabled')
    search_fields = ('user__username',)
    readonly_fields = ('password_changed_at',)
    exclude = ('totp_secret', 'totp_last_step')
    actions = ['force_password_change', 'reset_two_factor']

    @admin.action(description='Obriga troka password iha login tuir mai')
    def force_password_change(self, request, queryset):
        queryset.update(must_change_password=True)

    @admin.action(description='Reset verifikasaun pasu-2 (utilizador lakon telemovel)')
    def reset_two_factor(self, request, queryset):
        queryset.update(totp_enabled=False, totp_secret='', totp_last_step=0)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'username', 'action', 'model', 'object_repr', 'ip_address')
    list_filter = ('action', 'app_label', 'created_at')
    search_fields = ('username', 'model', 'object_repr')
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
