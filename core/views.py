from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from students.models import Student
from subjects.models import SubjectAssignment
from attendance.models import AttendanceRecord, AttendanceSession
from exams.models import Result, Exam
from finance.models import StudentFee
from faculty.models import Faculty
from courses.models import Course
from subjects.models import Subject
from notices.utils import get_dashboard_notices


@login_required
def dashboard(request):
    user = request.user
    role = getattr(user, "role", None)

    # ADMIN DASHBOARD
    if user.is_superuser or role == "admin":
        return render(request, "core/dashboard.html", {
            "dashboard_title": "Admin Dashboard",
            "student_count": Student.objects.count(),
            "faculty_count": Faculty.objects.count(),
            "course_count": Course.objects.count(),
            "subject_count": Subject.objects.count(),
            "attendance_count": AttendanceSession.objects.count(),
            "exam_count": Exam.objects.count(),
            "result_count": Result.objects.count(),
            "fee_count": StudentFee.objects.count(),
            "pending_fee_total": 0,
            "notices": get_dashboard_notices(request.user),
        })

    # STUDENT DASHBOARD
    elif role == "student":
        student = Student.objects.filter(user=user).first()

        subjects = SubjectAssignment.objects.none()
        attendance_records = AttendanceRecord.objects.none()
        results = Result.objects.none()
        fees = StudentFee.objects.none()

        if student:
            subjects = SubjectAssignment.objects.filter(
                department=student.department,
                course=student.course_fk,
                semester=student.semester,
                is_active=True
            )

            if student.section:
                subjects = subjects.filter(section__iexact=student.section)

            attendance_records = AttendanceRecord.objects.filter(student=student)
            results = Result.objects.filter(student=student)
            fees = StudentFee.objects.filter(student=student)

        return render(request, "core/student_dashboard.html", {
            "student": student,
            "subject_count": subjects.count(),
            "attendance_count": attendance_records.count(),
            "result_count": results.count(),
            "fee_count": fees.count(),
            "notices": get_dashboard_notices(request.user),
        })

    # FACULTY DASHBOARD
    elif role == "faculty":
        faculty = Faculty.objects.filter(user=user).first()

        assigned_subjects = SubjectAssignment.objects.none()
        recent_attendance = AttendanceSession.objects.none()

        if faculty:
            assigned_subjects = SubjectAssignment.objects.select_related(
                "department", "course", "subject", "faculty"
            ).filter(
                faculty=faculty,
                is_active=True
            ).order_by("semester", "section", "subject__name")

            recent_attendance = AttendanceSession.objects.select_related(
                "department", "course", "subject", "faculty"
            ).filter(
                faculty=faculty
            ).order_by("-date", "-lecture_number")[:5]

        return render(request, "core/faculty_dashboard.html", {
            "faculty": faculty,
            "subject_count": assigned_subjects.count(),
            "assigned_subjects": assigned_subjects,
            "recent_attendance": recent_attendance,
            "notices": get_dashboard_notices(request.user),
        })

    return render(request, "core/dashboard.html", {
        "dashboard_title": "Dashboard",
        "notices": get_dashboard_notices(request.user),
    })