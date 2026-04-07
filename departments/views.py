from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DepartmentForm
from .models import Department
from courses.models import Course
from faculty.models import Faculty
from students.models import Student
from subjects.models import SubjectAssignment


@login_required
def department_list(request):
    query = request.GET.get("q", "").strip()

    department_qs = Department.objects.all().order_by("name")

    if query:
        department_qs = department_qs.filter(
            Q(name__icontains=query) | Q(code__icontains=query)
        )

    paginator = Paginator(department_qs, 10)
    page_number = request.GET.get("page")
    departments = paginator.get_page(page_number)

    return render(request, "departments/department_list.html", {
        "departments": departments,
        "query": query,
    })


@login_required
def add_department(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Department added successfully.")
            return redirect("department_list")
    else:
        form = DepartmentForm()

    return render(request, "departments/add_department.html", {
        "form": form
    })


@login_required
def edit_department(request, pk):
    department = get_object_or_404(Department, pk=pk)

    if request.method == "POST":
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, "Department updated successfully.")
            return redirect("department_list")
    else:
        form = DepartmentForm(instance=department)

    return render(request, "departments/edit_department.html", {
        "form": form,
        "department": department,
    })


@login_required
def delete_department(request, pk):
    department = get_object_or_404(Department, pk=pk)

    related_courses_count = Course.objects.filter(department=department).count()
    related_faculty_count = Faculty.objects.filter(department=department).count()
    related_students_count = Student.objects.filter(department=department).count()
    related_assignments_count = SubjectAssignment.objects.filter(department=department).count()

    if request.method == "POST":
        if related_courses_count or related_faculty_count or related_students_count or related_assignments_count:
            messages.error(
                request,
                "Cannot delete this department because it is linked with courses, faculty, students, or subject assignments."
            )
            return redirect("department_profile", pk=department.id)

        department.delete()
        messages.success(request, "Department deleted successfully.")
        return redirect("department_list")

    return render(request, "departments/delete_department.html", {
        "department": department,
        "related_courses_count": related_courses_count,
        "related_faculty_count": related_faculty_count,
        "related_students_count": related_students_count,
        "related_assignments_count": related_assignments_count,
    })


@login_required
def department_profile(request, pk):
    department = get_object_or_404(Department, pk=pk)

    related_courses = Course.objects.filter(department=department).order_by("name")
    related_faculty = Faculty.objects.filter(department=department).order_by("name")
    related_students = Student.objects.filter(department=department).order_by("name")
    related_assignments = SubjectAssignment.objects.select_related(
        "subject", "course", "faculty"
    ).filter(
        department=department,
        is_active=True
    ).order_by("semester", "section", "subject__name")

    context = {
        "department": department,
        "related_courses": related_courses,
        "related_faculty": related_faculty,
        "related_students": related_students,
        "related_assignments": related_assignments,
        "course_count": related_courses.count(),
        "faculty_count": related_faculty.count(),
        "student_count": related_students.count(),
        "assignment_count": related_assignments.count(),
    }

    return render(request, "departments/department_profile.html", context)