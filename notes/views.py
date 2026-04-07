from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from faculty.models import Faculty
from students.models import Student
from subjects.models import SubjectAssignment
from .forms import NoteForm
from .models import Note


def is_faculty(user):
    return getattr(user, 'role', None) == 'faculty'


@login_required
def faculty_note_list(request):
    faculty = Faculty.objects.filter(user=request.user).first()

    if not faculty:
        messages.error(request, "Faculty profile not linked.")
        return redirect('dashboard')

    notes = Note.objects.select_related(
        'faculty', 'subject_assignment', 'subject_assignment__subject',
        'subject_assignment__course', 'subject_assignment__department'
    ).filter(
        faculty=faculty
    )

    return render(request, 'notes/faculty_note_list.html', {
        'notes': notes
    })


@login_required
def upload_note(request):
    faculty = Faculty.objects.filter(user=request.user).first()

    if not faculty:
        messages.error(request, "Faculty profile not linked.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES)
        form.fields['subject_assignment'].queryset = SubjectAssignment.objects.filter(
            faculty=faculty,
            is_active=True
        ).select_related('subject', 'course', 'department')

        if form.is_valid():
            note = form.save(commit=False)
            note.faculty = faculty
            note.save()
            messages.success(request, "Note uploaded successfully.")
            return redirect('faculty_note_list')
    else:
        form = NoteForm()
        form.fields['subject_assignment'].queryset = SubjectAssignment.objects.filter(
            faculty=faculty,
            is_active=True
        ).select_related('subject', 'course', 'department')

    return render(request, 'notes/upload_note.html', {
        'form': form
    })


@login_required
def edit_note(request, pk):
    faculty = Faculty.objects.filter(user=request.user).first()

    if not faculty:
        messages.error(request, "Faculty profile not linked.")
        return redirect('dashboard')

    note = get_object_or_404(Note, pk=pk, faculty=faculty)

    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES, instance=note)
        form.fields['subject_assignment'].queryset = SubjectAssignment.objects.filter(
            faculty=faculty,
            is_active=True
        ).select_related('subject', 'course', 'department')

        if form.is_valid():
            updated_note = form.save(commit=False)
            updated_note.faculty = faculty
            updated_note.save()
            messages.success(request, "Note updated successfully.")
            return redirect('faculty_note_list')
    else:
        form = NoteForm(instance=note)
        form.fields['subject_assignment'].queryset = SubjectAssignment.objects.filter(
            faculty=faculty,
            is_active=True
        ).select_related('subject', 'course', 'department')

    return render(request, 'notes/upload_note.html', {
        'form': form,
        'is_edit': True
    })


@login_required
def delete_note(request, pk):
    faculty = Faculty.objects.filter(user=request.user).first()

    if not faculty:
        messages.error(request, "Faculty profile not linked.")
        return redirect('dashboard')

    note = get_object_or_404(Note, pk=pk, faculty=faculty)

    if request.method == 'POST':
        note.delete()
        messages.success(request, "Note deleted successfully.")
        return redirect('faculty_note_list')

    return render(request, 'notes/delete_note.html', {
        'note': note
    })


@login_required
def student_note_list(request):
    student = Student.objects.filter(user=request.user).first()

    if not student:
        messages.error(request, "Student profile not found.")
        return redirect('dashboard')

    assignments = SubjectAssignment.objects.filter(
        department=student.department,
        course=student.course_fk,
        semester=student.semester,
        is_active=True
    )

    if student.section:
        assignments = assignments.filter(section__iexact=student.section)

    notes = Note.objects.select_related(
        'faculty', 'subject_assignment', 'subject_assignment__subject',
        'subject_assignment__course', 'subject_assignment__department'
    ).filter(
        subject_assignment__in=assignments,
        is_active=True
    )

    return render(request, 'notes/student_note_list.html', {
        'notes': notes
    })