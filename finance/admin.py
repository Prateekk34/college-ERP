from django.contrib import admin
from .models import FeeStructure, StudentFee, ExtraFee, FeeInstallment


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('course', 'academic_year', 'year', 'semester', 'total_amount', 'is_active')
    list_filter = ('academic_year', 'year', 'semester', 'is_active')
    search_fields = ('course__name', 'academic_year')


@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'academic_year', 'year', 'semester', 'base_amount', 'is_locked')
    list_filter = ('academic_year', 'year', 'semester', 'is_locked')
    search_fields = ('student__name', 'student__enrollment_number')


@admin.register(ExtraFee)
class ExtraFeeAdmin(admin.ModelAdmin):
    list_display = ('student_fee', 'title', 'amount', 'added_on')
    list_filter = ('added_on',)
    search_fields = ('title', 'student_fee__student__name')


@admin.register(FeeInstallment)
class FeeInstallmentAdmin(admin.ModelAdmin):
    list_display = ('student_fee', 'amount_paid', 'payment_date', 'payment_mode')
    list_filter = ('payment_date', 'payment_mode')
    search_fields = ('student_fee__student__name', 'reference_no')