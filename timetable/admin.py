from django.contrib import admin
from .models import Timetable


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = (
        'day',
        'lecture_number',
        'subject_assignment',
        'start_time',
        'end_time',
        'room',
        'is_active',
    )
    list_filter = ('day', 'is_active')
    search_fields = (
        'subject_assignment__subject__name',
        'subject_assignment__course__name',
        'subject_assignment__department__name',
        'room',
    )