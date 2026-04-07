from django.contrib import admin
from .models import Notice


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "target",
        "department",
        "course",
        "publish_date",
        "expiry_date",
        "is_active",
    )
    list_filter = ("target", "is_active", "department", "course")
    search_fields = ("title", "message")