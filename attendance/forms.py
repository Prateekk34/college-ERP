from django import forms
from .models import AttendanceSession
from courses.models import Course
from subjects.models import SubjectAssignment
from faculty.models import Faculty


SEMESTER_CHOICES = (
    (1, 'Semester 1'),
    (2, 'Semester 2'),
    (3, 'Semester 3'),
    (4, 'Semester 4'),
    (5, 'Semester 5'),
    (6, 'Semester 6'),
    (7, 'Semester 7'),
    (8, 'Semester 8'),
)


class AttendanceSessionForm(forms.ModelForm):
    semester = forms.ChoiceField(
        choices=SEMESTER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = AttendanceSession
        fields = [
            'department',
            'course',
            'semester',
            'section',
            'subject',
            'date',
            'lecture_number',
            'faculty',
        ]
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Example: A'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'lecture_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['course'].queryset = Course.objects.all().order_by('name')
        self.fields['faculty'].queryset = Faculty.objects.all().order_by('name')
        self.fields['subject'].queryset = SubjectAssignment.objects.none().values_list('subject', flat=True)

        # default empty subject queryset
        from subjects.models import Subject
        self.fields['subject'].queryset = Subject.objects.none()

        if self.instance.pk and self.instance.department:
            self.fields['course'].queryset = Course.objects.filter(
                department=self.instance.department
            ).order_by('name')

        department = None
        course = None
        semester = None
        section = None

        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['course'].queryset = Course.objects.filter(
                    department_id=department_id
                ).order_by('name')
                from departments.models import Department
                department = Department.objects.filter(id=department_id).first()
            except (ValueError, TypeError):
                pass

        if 'course' in self.data:
            try:
                course_id = int(self.data.get('course'))
                course = Course.objects.filter(id=course_id).first()
            except (ValueError, TypeError):
                pass

        if 'semester' in self.data:
            try:
                semester = int(self.data.get('semester'))
            except (ValueError, TypeError):
                pass

        section = self.data.get('section')

        if department and course and semester:
            assignment_qs = SubjectAssignment.objects.filter(
                department=department,
                course=course,
                semester=semester,
                is_active=True
            )

            if section:
                assignment_qs = assignment_qs.filter(section__iexact=section)
            else:
                assignment_qs = assignment_qs.filter(
                    section__isnull=True
                ) | SubjectAssignment.objects.filter(
                    department=department,
                    course=course,
                    semester=semester,
                    section='',
                    is_active=True
                )

            subject_ids = assignment_qs.values_list('subject_id', flat=True).distinct()
            faculty_ids = assignment_qs.values_list('faculty_id', flat=True).distinct()

            from subjects.models import Subject
            self.fields['subject'].queryset = Subject.objects.filter(
                id__in=subject_ids
            ).order_by('name')

            self.fields['faculty'].queryset = Faculty.objects.filter(
                id__in=faculty_ids
            ).order_by('name')

    def clean_semester(self):
        return int(self.cleaned_data.get('semester'))

    def clean(self):
        cleaned_data = super().clean()
        department = cleaned_data.get('department')
        course = cleaned_data.get('course')
        semester = cleaned_data.get('semester')
        section = cleaned_data.get('section')
        subject = cleaned_data.get('subject')
        faculty = cleaned_data.get('faculty')

        if department and course and course.department_id != department.id:
            self.add_error('course', 'Selected course does not belong to selected department.')

        if department and course and semester and subject:
            assignment_qs = SubjectAssignment.objects.filter(
                department=department,
                course=course,
                semester=semester,
                subject=subject,
                is_active=True
            )

            if section:
                assignment_qs = assignment_qs.filter(section__iexact=section)
            else:
                assignment_qs = assignment_qs.filter(section__isnull=True) | SubjectAssignment.objects.filter(
                    department=department,
                    course=course,
                    semester=semester,
                    subject=subject,
                    section='',
                    is_active=True
                )

            if not assignment_qs.exists():
                self.add_error('subject', 'This subject is not assigned for the selected class.')

            if faculty and assignment_qs.exists() and not assignment_qs.filter(faculty=faculty).exists():
                self.add_error('faculty', 'Selected faculty is not assigned to this subject/class.')

        return cleaned_data