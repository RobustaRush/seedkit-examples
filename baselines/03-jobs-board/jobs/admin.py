from django.contrib import admin

from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "is_active", "published_at")
    list_filter = ("is_active",)
    search_fields = ("title", "company")
