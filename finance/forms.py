from django import forms
from .models import FeeStructure, StudentFee, ExtraFee, FeeInstallment
from students.models import Student


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = [
            'department', 'course', 'academic_year', 'year', 'semester',
            'admission_fee', 'tuition_fee', 'exam_fee', 'library_fee',
            'lab_fee', 'other_fee', 'is_active'
        ]
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2025-26'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control'}),
            'admission_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tuition_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'exam_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'library_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'lab_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'other_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StudentFeeForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=Student.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = StudentFee
        fields = ['student', 'fee_structure', 'academic_year', 'year', 'semester', 'base_amount', 'notes', 'is_locked']
        widgets = {
            'fee_structure': forms.Select(attrs={'class': 'form-select'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control'}),
            'base_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_locked': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ExtraFeeForm(forms.ModelForm):
    class Meta:
        model = ExtraFee
        fields = ['title', 'amount', 'reason', 'added_on']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reason': forms.TextInput(attrs={'class': 'form-control'}),
            'added_on': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class FeeInstallmentForm(forms.ModelForm):
    class Meta:
        model = FeeInstallment
        fields = ['amount_paid', 'payment_date', 'payment_mode', 'reference_no', 'remarks', 'received_by']
        widgets = {
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_mode': forms.Select(attrs={'class': 'form-select'}),
            'reference_no': forms.TextInput(attrs={'class': 'form-control'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control'}),
            'received_by': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.student_fee = kwargs.pop('student_fee', None)
        super().__init__(*args, **kwargs)

    def clean_amount_paid(self):
        amount = self.cleaned_data['amount_paid']
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0.")

        if self.student_fee:
            pending = self.student_fee.pending_amount
            if self.instance.pk:
                pending += self.instance.amount_paid

            if amount > pending:
                raise forms.ValidationError(f"Amount cannot exceed pending fee ({pending}).")
        return amount


class PromoteStudentFeeForm(forms.Form):
    current_student_fee = forms.ModelChoiceField(
        queryset=StudentFee.objects.select_related('student').all().order_by('-academic_year'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    next_academic_year = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2026-27'})
    )
    next_year = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    next_semester = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )