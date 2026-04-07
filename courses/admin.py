from django.contrib import admin
from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = ("id", "name", "code", "department", "duration")

    search_fields = ("name", "code")

    list_filter = ("department",)






