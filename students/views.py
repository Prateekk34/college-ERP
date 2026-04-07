from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from departments.models import Department
from courses.models import Course
from .forms import StudentForm
from .models import Student


def is_admin(user):
    return user.is_superuser or getattr(user, 'role', None) == 'admin'


def is_faculty(user):
    return getattr(user, 'role', None) == 'faculty'


@login_required
def student_list(request):
    query = request.GET.get('q', '')
    department_id = request.GET.get('department', '')
    course_id = request.GET.get('course', '')
    semester = request.GET.get('semester', '')

    students = Student.objects.select_related('user', 'department', 'course_fk').all().order_by('name')

    if getattr(request.user, 'role', None) == 'student':
        students = students.filter(user=request.user)

    if query:
        students = students.filter(
            Q(name__icontains=query) |
            Q(enrollment_number__icontains=query) |
            Q(roll_number__icontains=query) |
            Q(course_fk__name__icontains=query) |
            Q(department__name__icontains=query)
        )

    if department_id:
        students = students.filter(department_id=department_id)

    if course_id:
        students = students.filter(course_fk_id=course_id)

    if semester:
        students = students.filter(semester=semester)

    departments = Department.objects.all().order_by('name')
    courses = Course.objects.all().order_by('name')

    context = {
        'students': students,
        'departments': departments,
        'courses': courses,
        'query': query,
        'selected_department': department_id,
        'selected_course': course_id,
        'selected_semester': semester,
    }
    return render(request, 'students/student_list.html', context)


@login_required
def student_add(request):
    if not (is_admin(request.user) or is_faculty(request.user)):
        return redirect('student_list')

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Student added successfully.")
            return redirect('student_list')
    else:
        form = StudentForm()

    return render(request, 'students/add_student.html', {'form': form})


@login_required
def student_edit(request, pk):
    if not (is_admin(request.user) or is_faculty(request.user)):
        return redirect('student_list')

    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully.")
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)

    return render(request, 'students/add_student.html', {'form': form})


@login_required
def student_delete(request, pk):
    if not is_admin(request.user):
        return redirect('student_list')

    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        student.delete()
        messages.success(request, "Student deleted successfully.")
        return redirect('student_list')

    return render(request, 'students/student_confirm_delete.html', {'student': student})


@login_required
def student_profile(request, pk=None):
    if getattr(request.user, 'role', None) == 'student':
        student = get_object_or_404(
            Student.objects.select_related('user', 'department', 'course_fk'),
            user=request.user
        )
    else:
        student = get_object_or_404(
            Student.objects.select_related('user', 'department', 'course_fk'),
            pk=pk
        )

    return render(request, 'students/student_profile.html', {'student': student})