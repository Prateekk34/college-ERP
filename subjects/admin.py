from django.contrib import admin
from .models import Subject, SubjectAssignment


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(SubjectAssignment)
class SubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        'department',
        'course',
        'semester',
        'section',
        'subject',
        'faculty',
        'is_active',
    )
    list_filter = ('department', 'course', 'semester', 'section', 'is_active')
    search_fields = (
        'subject__name',
        'subject__code',
        'faculty__name',
        'course__name',
        'department__name',
    )