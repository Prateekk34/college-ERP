from django.contrib import admin
from .models import AttendanceSession, AttendanceRecord


class AttendanceRecordInline(admin.TabularInline):
    model = AttendanceRecord
    extra = 0


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'lecture_number',
        'department',
        'course',
        'semester',
        'section',
        'subject',
        'faculty',
    )
    list_filter = (
        'department',
        'course',
        'semester',
        'section',
        'subject',
        'date',
    )
    search_fields = (
        'department__name',
        'course__name',
        'subject__name',
        'faculty__name',
    )
    inlines = [AttendanceRecordInline]


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'status')
    list_filter = ('status', 'session__date', 'session__subject')
    search_fields = ('student__name', 'student__enrollment_number')