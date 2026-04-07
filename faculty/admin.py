from django.contrib import admin
from .models import Faculty


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'user',
        'email',
        'department',
        'course',
        'designation',
    )
    list_filter = ('department', 'course', 'designation')
    search_fields = ('name', 'email', 'user__username')