from django.contrib import admin

from .models import JobPost


@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ["title", "company", "location", "is_active", "posted_at"]
    list_filter = ["is_active", "posted_at"]
    search_fields = ["title", "company", "location"]
