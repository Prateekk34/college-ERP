from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from departments.models import Department
from courses.models import Course
from students.models import Student
from .forms import SubjectForm, SubjectAssignmentForm
from .models import Subject, SubjectAssignment


def is_admin(user):
    return user.is_superuser or getattr(user, 'role', None) == 'admin'


def is_faculty(user):
    return getattr(user, 'role', None) == 'faculty'


@login_required
def subject_list(request):
    query = request.GET.get('q', '')
    subjects = Subject.objects.all().order_by('name')

    if query:
        subjects = subjects.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query)
        )

    return render(request, 'subjects/subject_list.html', {
        'subjects': subjects,
        'query': query,
    })


@login_required
def subject_add(request):
    if not (is_admin(request.user) or is_faculty(request.user)):
        return redirect('subject_list')

    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject added successfully.')
            return redirect('subject_list')
    else:
        form = SubjectForm()

    return render(request, 'subjects/subject_form.html', {'form': form})


@login_required
def subject_edit(request, pk):
    if not (is_admin(request.user) or is_faculty(request.user)):
        return redirect('subject_list')

    subject = get_object_or_404(Subject, pk=pk)

    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully.')
            return redirect('subject_list')
    else:
        form = SubjectForm(instance=subject)

    return render(request, 'subjects/subject_form.html', {'form': form})


@login_required
def subject_delete(request, pk):
    if not is_admin(request.user):
        return redirect('subject_list')

    subject = get_object_or_404(Subject, pk=pk)

    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted successfully.')
        return redirect('subject_list')

    return render(request, 'subjects/subject_confirm_delete.html', {'subject': subject})


@login_required
def subject_assignment_list(request):
    query = request.GET.get('q', '')
    department_id = request.GET.get('department', '')
    course_id = request.GET.get('course', '')
    semester = request.GET.get('semester', '')

    assignments = SubjectAssignment.objects.select_related(
        'department', 'course', 'subject', 'faculty'
    ).all().order_by('department__name', 'course__name', 'semester', 'section', 'subject__name')

    if query:
        assignments = assignments.filter(
            Q(subject__name__icontains=query) |
            Q(subject__code__icontains=query) |
            Q(faculty__name__icontains=query) |
            Q(course__name__icontains=query) |
            Q(department__name__icontains=query)
        )

    if department_id:
        assignments = assignments.filter(department_id=department_id)

    if course_id:
        assignments = assignments.filter(course_id=course_id)

    if semester:
        assignments = assignments.filter(semester=semester)

    departments = Department.objects.all().order_by('name')
    courses = Course.objects.all().order_by('name')

    return render(request, 'subjects/subject_assignment_list.html', {
        'assignments': assignments,
        'departments': departments,
        'courses': courses,
        'query': query,
        'selected_department': department_id,
        'selected_course': course_id,
        'selected_semester': semester,
    })


@login_required
def subject_assignment_add(request):
    if not (is_admin(request.user) or is_faculty(request.user)):
        return redirect('subject_assignment_list')

    if request.method == 'POST':
        form = SubjectAssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject assigned successfully.')
            return redirect('subject_assignment_list')
    else:
        form = SubjectAssignmentForm()

    return render(request, 'subjects/subject_assignment_form.html', {'form': form})


@login_required
def subject_assignment_edit(request, pk):
    if not (is_admin(request.user) or is_faculty(request.user)):
        return redirect('subject_assignment_list')

    assignment = get_object_or_404(SubjectAssignment, pk=pk)

    if request.method == 'POST':
        form = SubjectAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject assignment updated successfully.')
            return redirect('subject_assignment_list')
    else:
        form = SubjectAssignmentForm(instance=assignment)

    return render(request, 'subjects/subject_assignment_form.html', {
        'form': form,
        'assignment': assignment,
    })


@login_required
def subject_assignment_delete(request, pk):
    if not is_admin(request.user):
        return redirect('subject_assignment_list')

    assignment = get_object_or_404(SubjectAssignment, pk=pk)

    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Subject assignment deleted successfully.')
        return redirect('subject_assignment_list')

    return render(request, 'subjects/subject_assignment_confirm_delete.html', {
        'assignment': assignment,
    })


@login_required
def my_subjects(request):
    if getattr(request.user, 'role', None) != 'student':
        return redirect('dashboard')

    student = get_object_or_404(
        Student.objects.select_related('department', 'course_fk'),
        user=request.user
    )

    assignments = SubjectAssignment.objects.select_related(
        'department', 'course', 'subject', 'faculty'
    ).filter(
        department=student.department,
        course=student.course_fk,
        semester=student.semester,
        is_active=True,
    ).order_by('subject__name')

    if student.section:
        assignments = assignments.filter(
            Q(section__iexact=student.section) | Q(section__isnull=True) | Q(section__exact='')
        )

    return render(request, 'subjects/my_subjects.html', {
        'student': student,
        'assignments': assignments,
    })