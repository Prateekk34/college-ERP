from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from faculty.models import Faculty
from students.models import Student
from .forms import TimetableForm
from .models import Timetable


def is_faculty(user):
    return getattr(user, 'role', None) == 'faculty'


@login_required
def timetable_list(request):
    timetables = Timetable.objects.select_related(
        'subject_assignment',
        'subject_assignment__subject',
        'subject_assignment__course',
        'subject_assignment__department',
        'subject_assignment__faculty',
    ).filter(
        is_active=True
    ).order_by('day', 'lecture_number')

    return render(request, 'timetable/timetable_list.html', {
        'timetables': timetables
    })


@login_required
def add_timetable(request):
    if request.method == 'POST':
        form = TimetableForm(request.POST, faculty_user=request.user if is_faculty(request.user) else None)
        if form.is_valid():
            form.save()
            messages.success(request, "Timetable entry added successfully.")
            return redirect('timetable_list')
    else:
        form = TimetableForm(faculty_user=request.user if is_faculty(request.user) else None)

    return render(request, 'timetable/timetable_form.html', {
        'form': form
    })


@login_required
def edit_timetable(request, pk):
    timetable = get_object_or_404(Timetable, pk=pk)

    if request.method == 'POST':
        form = TimetableForm(request.POST, instance=timetable, faculty_user=request.user if is_faculty(request.user) else None)
        if form.is_valid():
            form.save()
            messages.success(request, "Timetable updated successfully.")
            return redirect('timetable_list')
    else:
        form = TimetableForm(instance=timetable, faculty_user=request.user if is_faculty(request.user) else None)

    return render(request, 'timetable/timetable_form.html', {
        'form': form,
        'is_edit': True
    })


@login_required
def delete_timetable(request, pk):
    timetable = get_object_or_404(Timetable, pk=pk)

    if request.method == 'POST':
        timetable.delete()
        messages.success(request, "Timetable deleted successfully.")
        return redirect('timetable_list')

    return render(request, 'timetable/delete_timetable.html', {
        'timetable': timetable
    })


@login_required
def faculty_timetable(request):
    faculty = Faculty.objects.filter(user=request.user).first()

    if not faculty:
        messages.error(request, "Faculty profile not linked.")
        return redirect('dashboard')

    timetables = Timetable.objects.select_related(
        'subject_assignment',
        'subject_assignment__subject',
        'subject_assignment__course',
        'subject_assignment__department',
        'subject_assignment__faculty',
    ).filter(
        subject_assignment__faculty=faculty,
        is_active=True
    ).order_by('day', 'lecture_number')

    return render(request, 'timetable/faculty_timetable.html', {
        'timetables': timetables,
        'faculty': faculty,
    })


@login_required
def student_timetable(request):
    student = Student.objects.filter(user=request.user).first()

    if not student:
        messages.error(request, "Student profile not found.")
        return redirect('dashboard')

    timetables = Timetable.objects.select_related(
        'subject_assignment',
        'subject_assignment__subject',
        'subject_assignment__course',
        'subject_assignment__department',
        'subject_assignment__faculty',
    ).filter(
        subject_assignment__department=student.department,
        subject_assignment__course=student.course_fk,
        subject_assignment__semester=student.semester,
        is_active=True
    ).order_by('day', 'lecture_number')

    if student.section:
        timetables = timetables.filter(subject_assignment__section__iexact=student.section)

    return render(request, 'timetable/student_timetable.html', {
        'timetables': timetables,
        'student': student,
    })