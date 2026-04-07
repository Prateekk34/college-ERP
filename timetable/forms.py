from django import forms
from .models import Timetable
from subjects.models import SubjectAssignment
from faculty.models import Faculty


class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = [
            'subject_assignment',
            'day',
            'lecture_number',
            'start_time',
            'end_time',
            'room',
            'is_active',
        ]
        widgets = {
            'subject_assignment': forms.Select(attrs={'class': 'form-select'}),
            'day': forms.Select(attrs={'class': 'form-select'}),
            'lecture_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Example: Room 101'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        faculty_user = kwargs.pop('faculty_user', None)
        super().__init__(*args, **kwargs)

        self.fields['subject_assignment'].queryset = SubjectAssignment.objects.select_related(
            'subject', 'course', 'department', 'faculty'
        ).filter(
            is_active=True
        ).order_by('course__name', 'semester', 'subject__name')

        if faculty_user:
            faculty = Faculty.objects.filter(user=faculty_user).first()
            if faculty:
                self.fields['subject_assignment'].queryset = SubjectAssignment.objects.select_related(
                    'subject', 'course', 'department', 'faculty'
                ).filter(
                    faculty=faculty,
                    is_active=True
                ).order_by('course__name', 'semester', 'subject__name')