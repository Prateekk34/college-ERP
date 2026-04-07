from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from students.models import Student
from faculty.models import Faculty
from departments.models import Department
from courses.models import Course

from .models import Notice
from .forms import NoticeForm


def _safe_department_obj(raw_department):
    """
    Old dirty data ko safe handle karega.
    Agar raw_department already Department object hai to wahi return.
    Agar string hai (jaise 'cse'), to Department name/code se match karega.
    """
    if not raw_department:
        return None

    if isinstance(raw_department, Department):
        return raw_department

    try:
        dept_id = int(raw_department)
        return Department.objects.filter(id=dept_id).first()
    except (TypeError, ValueError):
        pass

    raw_text = str(raw_department).strip()

    dept = Department.objects.filter(name__iexact=raw_text).first()
    if dept:
        return dept

    dept = Department.objects.filter(code__iexact=raw_text).first()
    if dept:
        return dept

    return None


def _safe_course_obj(raw_course):
    """
    Old dirty data ko safe handle karega.
    """
    if not raw_course:
        return None

    if isinstance(raw_course, Course):
        return raw_course

    try:
        course_id = int(raw_course)
        return Course.objects.filter(id=course_id).first()
    except (TypeError, ValueError):
        pass

    raw_text = str(raw_course).strip()

    course = Course.objects.filter(name__iexact=raw_text).first()
    if course:
        return course

    course = Course.objects.filter(code__iexact=raw_text).first()
    if course:
        return course

    return None


def get_visible_notices_for_user(user):
    notices = Notice.objects.filter(
        is_active=True,
        publish_date__lte=timezone.now()
    ).exclude(
        expiry_date__isnull=False,
        expiry_date__lt=timezone.now()
    )

    if user.is_superuser or getattr(user, "role", None) == "admin":
        return notices.order_by("-publish_date", "-id")

    role = getattr(user, "role", None)

    if role == "student":
        student = Student.objects.filter(user=user).select_related("department", "course_fk").first()

        filtered = notices.filter(target__in=["all", "students"])

        if student:
            dept = student.department
            course = student.course_fk

            q = Q(department__isnull=True)
            if dept:
                q |= Q(department=dept)

            c = Q(course__isnull=True)
            if course:
                c |= Q(course=course)

            filtered = filtered.filter(q).filter(c)

        return filtered.distinct().order_by("-publish_date", "-id")

    elif role == "faculty":
        faculty = Faculty.objects.filter(user=user).first()

        filtered = notices.filter(target__in=["all", "faculty"])

        if faculty:
            dept = _safe_department_obj(getattr(faculty, "department", None))
            course = _safe_course_obj(getattr(faculty, "course", None))

            q = Q(department__isnull=True)
            if dept:
                q |= Q(department=dept)

            c = Q(course__isnull=True)
            if course:
                c |= Q(course=course)

            filtered = filtered.filter(q).filter(c)

        return filtered.distinct().order_by("-publish_date", "-id")

    return notices.filter(target="all").order_by("-publish_date", "-id")


@login_required
def notice_list(request):
    if request.user.is_superuser or getattr(request.user, "role", None) == "admin":
        notices = Notice.objects.all().order_by("-publish_date", "-id")
    else:
        notices = get_visible_notices_for_user(request.user)

    return render(request, "notices/notice_list.html", {
        "notices": notices
    })


@login_required
def notice_add(request):
    if not (request.user.is_superuser or getattr(request.user, "role", None) == "admin"):
        messages.error(request, "Only admin can add notices.")
        return redirect("notice_list")

    if request.method == "POST":
        form = NoticeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Notice added successfully.")
            return redirect("notice_list")
    else:
        form = NoticeForm()

    return render(request, "notices/notice_form.html", {
        "form": form,
        "page_title_custom": "Add Notice"
    })


@login_required
def notice_edit(request, pk):
    if not (request.user.is_superuser or getattr(request.user, "role", None) == "admin"):
        messages.error(request, "Only admin can edit notices.")
        return redirect("notice_list")

    notice = get_object_or_404(Notice, pk=pk)

    if request.method == "POST":
        form = NoticeForm(request.POST, instance=notice)
        if form.is_valid():
            form.save()
            messages.success(request, "Notice updated successfully.")
            return redirect("notice_list")
    else:
        form = NoticeForm(instance=notice)

    return render(request, "notices/notice_form.html", {
        "form": form,
        "page_title_custom": "Edit Notice"
    })


@login_required
def notice_delete(request, pk):
    if not (request.user.is_superuser or getattr(request.user, "role", None) == "admin"):
        messages.error(request, "Only admin can delete notices.")
        return redirect("notice_list")

    notice = get_object_or_404(Notice, pk=pk)

    if request.method == "POST":
        notice.delete()
        messages.success(request, "Notice deleted successfully.")
        return redirect("notice_list")

    return render(request, "notices/notice_delete.html", {
        "notice": notice
    })