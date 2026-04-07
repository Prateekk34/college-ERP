from django import forms
from .models import ExamType, Exam, ExamSchedule
from subjects.models import SubjectAssignment
from faculty.models import Faculty


class ExamTypeForm(forms.ModelForm):
    class Meta:
        model = ExamType
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = [
            'department',
            'course',
            'semester',
            'section',
            'exam_type',
            'title',
            'total_marks',
            'start_date',
            'end_date',
            'exam_date',
            'is_active',
        ]
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control'}),
            'section': forms.TextInput(attrs={'class': 'form-control'}),
            'exam_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'exam_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ExamScheduleForm(forms.ModelForm):
    class Meta:
        model = ExamSchedule
        fields = [
            'exam',
            'subject_assignment',
            'paper_date',
            'start_time',
            'end_time',
            'room',
            'max_marks',
        ]
        widgets = {
            'exam': forms.Select(attrs={'class': 'form-select'}),
            'subject_assignment': forms.Select(attrs={'class': 'form-select'}),
            'paper_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'room': forms.TextInput(attrs={'class': 'form-control'}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        faculty_user = kwargs.pop('faculty_user', None)
        super().__init__(*args, **kwargs)

        self.fields['subject_assignment'].queryset = SubjectAssignment.objects.select_related(
            'subject', 'course', 'department', 'faculty'
        ).filter(is_active=True)

        if faculty_user:
            faculty = Faculty.objects.filter(user=faculty_user).first()
            if faculty:
                self.fields['subject_assignment'].queryset = SubjectAssignment.objects.select_related(
                    'subject', 'course', 'department', 'faculty'
                ).filter(
                    faculty=faculty,
                    is_active=True
                )