from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'enrollment_number',
        'roll_number',
        'department',
        'course_fk',
        'semester',
        'year',
        'section',
    )
    list_filter = ('department', 'course_fk', 'semester', 'year', 'gender')
    search_fields = (
        'name',
        'enrollment_number',
        'roll_number',
        'department__name',
        'course_fk__name',
        'user__username',
    )