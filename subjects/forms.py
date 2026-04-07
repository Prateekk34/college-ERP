from django import forms
from .models import Subject, SubjectAssignment
from courses.models import Course
from faculty.models import Faculty


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SubjectAssignmentForm(forms.ModelForm):
    class Meta:
        model = SubjectAssignment
        fields = [
            'department',
            'course',
            'semester',
            'section',
            'subject',
            'faculty',
            'is_active',
        ]
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Example: A'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['course'].queryset = Course.objects.all().order_by('name')
        self.fields['faculty'].queryset = Faculty.objects.all().order_by('name')
        self.fields['subject'].queryset = Subject.objects.all().order_by('name')

        if self.instance.pk and self.instance.department:
            self.fields['course'].queryset = Course.objects.filter(
                department=self.instance.department
            ).order_by('name')

            self.fields['faculty'].queryset = Faculty.objects.filter(
                department__iexact=self.instance.department.name
            ).order_by('name')

        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                course_qs = Course.objects.filter(
                    department_id=department_id
                ).order_by('name')
                self.fields['course'].queryset = course_qs

                selected_department = None
                first_course = course_qs.first()
                if first_course:
                    selected_department = first_course.department
                else:
                    from departments.models import Department
                    selected_department = Department.objects.filter(id=department_id).first()

                if selected_department:
                    self.fields['faculty'].queryset = Faculty.objects.filter(
                        department__iexact=selected_department.name
                    ).order_by('name')
            except (ValueError, TypeError):
                self.fields['course'].queryset = Course.objects.all().order_by('name')
                self.fields['faculty'].queryset = Faculty.objects.all().order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        department = cleaned_data.get('department')
        course = cleaned_data.get('course')
        faculty = cleaned_data.get('faculty')

        if department and course and course.department_id != department.id:
            self.add_error('course', 'Selected course does not belong to selected department.')

        if department and faculty:
            faculty_department_value = getattr(faculty, 'department', None)
            if faculty_department_value and str(faculty_department_value).strip().lower() != str(department.name).strip().lower():
                self.add_error('faculty', 'Selected faculty does not belong to selected department.')

        return cleaned_data