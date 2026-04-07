from django import forms
from .models import Student
from courses.models import Course


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'user',
            'name',
            'enrollment_number',
            'roll_number',
            'department',
            'course_fk',
            'semester',
            'year',
            'section',
            'phone',
            'address',
            'date_of_birth',
            'gender',
            'photo',
            'admission_date',
        ]
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'enrollment_number': forms.TextInput(attrs={'class': 'form-control'}),
            'roll_number': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'course_fk': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'admission_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'course_fk': 'Course',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['course_fk'].queryset = Course.objects.none()

        if self.instance.pk and self.instance.department:
            self.fields['course_fk'].queryset = Course.objects.filter(
                department=self.instance.department
            ).order_by('name')

        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['course_fk'].queryset = Course.objects.filter(
                    department_id=department_id
                ).order_by('name')
            except (ValueError, TypeError):
                self.fields['course_fk'].queryset = Course.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        department = cleaned_data.get('department')
        course_fk = cleaned_data.get('course_fk')

        if department and course_fk and course_fk.department != department:
            self.add_error('course_fk', 'Selected course does not belong to selected department.')

        return cleaned_data

    def save(self, commit=True):
        student = super().save(commit=False)

        if student.course_fk:
            student.course = student.course_fk.name
            student.department = student.course_fk.department

        if commit:
            student.save()
            self.save_m2m()

        return student