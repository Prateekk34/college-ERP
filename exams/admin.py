from django.contrib import admin
from .models import ExamType, Exam, Result


@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'exam_type', 'course', 'semester', 'section', 'total_marks', 'exam_date', 'is_active')
    list_filter = ('exam_type', 'course', 'semester', 'is_active')
    search_fields = ('title', 'course__name', 'department__name')


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject_assignment', 'exam', 'marks_obtained')
    list_filter = ('exam', 'subject_assignment__course', 'subject_assignment__semester')
    search_fields = ('student__name', 'student__enrollment_number', 'subject_assignment__subject__name')