from django.contrib import admin

from .models import Announcement, Slide


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'publish_date', 'is_published')
    list_filter = ('level', 'is_published')
    list_editable = ('is_published',)
    search_fields = ('title', 'body')
    fieldsets = (
        (None, {'fields': ('title', 'body', 'level', 'publish_date', 'is_published')}),
        ('Tradusaun (opsionál)', {'classes': ('collapse',),
                                  'fields': ('title_pt', 'body_pt', 'title_en', 'body_en', 'title_id', 'body_id')}),
    )


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    fieldsets = (
        (None, {'fields': ('title', 'subtitle', 'image', 'order', 'is_active')}),
        ('Tradusaun (opsionál)', {'classes': ('collapse',),
                                  'fields': ('title_pt', 'subtitle_pt', 'title_en', 'subtitle_en',
                                             'title_id', 'subtitle_id')}),
    )
