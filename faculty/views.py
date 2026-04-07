from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Faculty
from .forms import FacultyForm
from subjects.models import SubjectAssignment
from attendance.models import AttendanceSession
from core.decorators import role_required


@login_required
@role_required(['faculty'])
def faculty_list(request):
    query = request.GET.get('q')

    if query:
        faculty_qs = Faculty.objects.filter(name__icontains=query).order_by('id')
    else:
        faculty_qs = Faculty.objects.all().order_by('id')

    paginator = Paginator(faculty_qs, 5)
    page_number = request.GET.get('page')
    faculties = paginator.get_page(page_number)

    return render(request, 'faculty/faculty_list.html', {'faculties': faculties})


@login_required
@role_required(['faculty'])
def add_faculty(request):
    if request.method == "POST":
        form = FacultyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Faculty added successfully.")
            return redirect('faculty_list')
    else:
        form = FacultyForm()

    return render(request, 'faculty/add_faculty.html', {'form': form})


@login_required
@role_required(['faculty'])
def edit_faculty(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)

    if request.method == "POST":
        form = FacultyForm(request.POST, request.FILES, instance=faculty)
        if form.is_valid():
            form.save()
            messages.success(request, "Faculty updated successfully.")
            return redirect('faculty_list')
    else:
        form = FacultyForm(instance=faculty)

    return render(request, 'faculty/edit_faculty.html', {'form': form})


@login_required
@role_required(['faculty'])
def delete_faculty(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)

    if request.method == "POST":
        faculty.delete()
        messages.success(request, "Faculty deleted successfully.")
        return redirect("faculty_list")

    return render(request, "faculty/delete_faculty.html", {"faculty": faculty})


@login_required
@role_required(['faculty'])
def faculty_profile(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)

    assigned_subjects = SubjectAssignment.objects.select_related(
        "department", "course", "subject", "faculty"
    ).filter(
        faculty=faculty,
        is_active=True
    ).order_by("semester", "section", "subject__name")

    attendance_sessions = AttendanceSession.objects.select_related(
        "department", "course", "subject", "faculty"
    ).filter(
        faculty=faculty
    ).order_by("-date", "-lecture_number")[:10]

    return render(request, "faculty/faculty_profile.html", {
        "faculty": faculty,
        "assigned_subjects": assigned_subjects,
        "attendance_sessions": attendance_sessions,
    })


@login_required
@role_required(['faculty'])
def my_faculty_profile(request):
    faculty = Faculty.objects.filter(user=request.user).first()

    if not faculty:
        messages.error(request, "Faculty profile is not linked with this login user.")
        return redirect("dashboard")

    assigned_subjects = SubjectAssignment.objects.select_related(
        "department", "course", "subject", "faculty"
    ).filter(
        faculty=faculty,
        is_active=True
    ).order_by("semester", "section", "subject__name")

    attendance_sessions = AttendanceSession.objects.select_related(
        "department", "course", "subject", "faculty"
    ).filter(
        faculty=faculty
    ).order_by("-date", "-lecture_number")[:10]

    return render(request, "faculty/faculty_profile.html", {
        "faculty": faculty,
        "assigned_subjects": assigned_subjects,
        "attendance_sessions": attendance_sessions,
    })


@login_required
@role_required(['faculty'])
def my_assigned_subjects(request):
    faculty = Faculty.objects.filter(user=request.user).first()

    if not faculty:
        messages.error(request, "Faculty profile is not linked with this login user.")
        return redirect("dashboard")

    assigned_subjects = SubjectAssignment.objects.select_related(
        "department", "course", "subject", "faculty"
    ).filter(
        faculty=faculty,
        is_active=True
    ).order_by("semester", "section", "subject__name")

    return render(request, "faculty/my_assigned_subjects.html", {
        "faculty": faculty,
        "assigned_subjects": assigned_subjects,
    })