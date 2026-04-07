from django.contrib import admin
from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'faculty', 'subject_assignment', 'uploaded_at', 'is_active')
    list_filter = ('is_active', 'uploaded_at', 'subject_assignment__course')
    search_fields = ('title', 'faculty__name', 'subject_assignment__subject__name')