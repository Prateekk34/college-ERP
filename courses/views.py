from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from .models import Course
from .forms import CourseForm
from students.models import Student
from subjects.models import SubjectAssignment


@login_required
def course_list(request):

    query = request.GET.get("q", "")

    courses = Course.objects.select_related(
        "department", "faculty"
    ).all().order_by("id")

    if query:
        courses = courses.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query)
        )

    paginator = Paginator(courses, 10)

    page_number = request.GET.get("page")

    courses = paginator.get_page(page_number)

    return render(request, "courses/course_list.html", {
        "courses": courses,
        "query": query,
    })


@login_required
def add_course(request):

    if request.method == "POST":

        form = CourseForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(request, "Course added successfully.")

            return redirect("course_list")

    else:

        form = CourseForm()

    return render(request, "courses/add_course.html", {
        "form": form
    })


@login_required
def edit_course(request, pk):

    course = get_object_or_404(Course, pk=pk)

    if request.method == "POST":

        form = CourseForm(request.POST, instance=course)

        if form.is_valid():
            form.save()

            messages.success(request, "Course updated successfully.")

            return redirect("course_list")

    else:

        form = CourseForm(instance=course)

    return render(request, "courses/edit_course.html", {
        "form": form,
        "course": course
    })


@login_required
def delete_course(request, pk):

    course = get_object_or_404(Course, pk=pk)

    student_count = Student.objects.filter(course_fk=course).count()

    assignment_count = SubjectAssignment.objects.filter(course=course).count()

    if request.method == "POST":

        if student_count > 0 or assignment_count > 0:

            messages.error(
                request,
                "Cannot delete this course because students or subjects are linked."
            )

            return redirect("course_profile", pk=course.id)

        course.delete()

        messages.success(request, "Course deleted successfully.")

        return redirect("course_list")

    return render(request, "courses/delete_course.html", {
        "course": course,
        "student_count": student_count,
        "assignment_count": assignment_count
    })


@login_required
def course_profile(request, pk):

    course = get_object_or_404(
        Course.objects.select_related("department", "faculty"),
        pk=pk
    )

    related_students = Student.objects.select_related(
        "department", "course_fk", "user"
    ).filter(
        course_fk=course
    ).order_by("name")

    related_assignments = SubjectAssignment.objects.select_related(
        "subject", "department", "course", "faculty"
    ).filter(
        course=course,
        is_active=True
    ).order_by("semester", "section", "subject__name")

    return render(request, "courses/course_profile.html", {
        "course": course,
        "related_students": related_students,
        "related_assignments": related_assignments,
    })