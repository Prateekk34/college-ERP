from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render

from students.models import Student
from .forms import AttendanceSessionForm
from .models import AttendanceSession, AttendanceRecord
from faculty.models import Faculty


def is_admin(user):
    return user.is_superuser or getattr(user, 'role', None) == 'admin'


def is_faculty(user):
    return getattr(user, 'role', None) == 'faculty'


@login_required
def attendance_list(request):
    query = request.GET.get('q', '')
    department_id = request.GET.get('department', '')
    course_id = request.GET.get('course', '')
    date = request.GET.get('date', '')

    sessions = AttendanceSession.objects.select_related(
        'department', 'course', 'subject', 'faculty'
    ).annotate(
        total_records=Count('records')
    ).order_by('-date', '-lecture_number')

    if getattr(request.user, 'role', None) == 'student':
        sessions = sessions.filter(records__student__user=request.user).distinct()

    if query:
        sessions = sessions.filter(
            Q(subject__name__icontains=query) |
            Q(course__name__icontains=query) |
            Q(department__name__icontains=query) |
            Q(section__icontains=query)
        )

    if department_id:
        sessions = sessions.filter(department_id=department_id)

    if course_id:
        sessions = sessions.filter(course_id=course_id)

    if date:
        sessions = sessions.filter(date=date)

    context = {
        'sessions': sessions,
        'query': query,
        'selected_department': department_id,
        'selected_course': course_id,
        'selected_date': date,
    }
    return render(request, 'attendance/attendance_list.html', context)


@login_required
def mark_attendance(request):
    if not (is_admin(request.user) or is_faculty(request.user)):
        return redirect('attendance_list')

    students = None
    faculty_instance = None

    if is_faculty(request.user):
        faculty_instance = Faculty.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = AttendanceSessionForm(request.POST)

        if faculty_instance:
            form.fields['faculty'].required = False

        if form.is_valid():
            department = form.cleaned_data['department']
            course = form.cleaned_data['course']
            semester = form.cleaned_data['semester']
            section = form.cleaned_data['section']
            subject = form.cleaned_data['subject']
            date = form.cleaned_data['date']
            lecture_number = form.cleaned_data['lecture_number']
            selected_faculty = faculty_instance if faculty_instance else form.cleaned_data.get('faculty')

            students = Student.objects.select_related('department', 'course_fk').filter(
                department=department,
                course_fk=course,
                semester=semester
            ).order_by('name')

            if section:
                students = students.filter(section__iexact=section)

            if 'save_attendance' in request.POST:
                session, created = AttendanceSession.objects.get_or_create(
                    department=department,
                    course=course,
                    semester=semester,
                    section=section,
                    subject=subject,
                    date=date,
                    lecture_number=lecture_number,
                    defaults={'faculty': selected_faculty}
                )

                if not created:
                    session.faculty = selected_faculty
                    session.subject = subject
                    session.save()

                for student in students:
                    status = request.POST.get(f'status_{student.id}', 'Absent')
                    AttendanceRecord.objects.update_or_create(
                        session=session,
                        student=student,
                        defaults={'status': status}
                    )

                messages.success(request, 'Attendance saved successfully.')
                return redirect('attendance_session_detail', pk=session.pk)
    else:
        form = AttendanceSessionForm()
        if faculty_instance:
            form.fields['faculty'].required = False
            form.initial['faculty'] = faculty_instance

    return render(request, 'attendance/mark_attendance.html', {
        'form': form,
        'students': students,
    })



@login_required
def attendance_session_detail(request, pk):
    session = get_object_or_404(
        AttendanceSession.objects.select_related(
            'department', 'course', 'subject', 'faculty'
        ),
        pk=pk
    )

    records = AttendanceRecord.objects.select_related('student').filter(
        session=session
    ).order_by('student__name')

    if getattr(request.user, 'role', None) == 'student':
        records = records.filter(student__user=request.user)

    context = {
        'session': session,
        'records': records,
    }
    return render(request, 'attendance/attendance_session_detail.html', context)


@login_required
def my_attendance(request):
    if getattr(request.user, 'role', None) != 'student':
        return redirect('attendance_list')

    records = AttendanceRecord.objects.select_related(
        'session', 'session__subject', 'session__course', 'session__department'
    ).filter(
        student__user=request.user
    ).order_by('-session__date', '-session__lecture_number')

    context = {
        'records': records,
    }
    return render(request, 'attendance/my_attendance.html', context)



@login_required
def attendance_session_detail(request, pk):

    session = get_object_or_404(AttendanceSession, pk=pk)

    records = AttendanceRecord.objects.filter(
        session=session
    ).select_related('student').order_by('student__name')

    return render(request, 'attendance/session_detail.html', {
        'session': session,
        'records': records
    })


@login_required
def edit_attendance(request, pk):

    session = get_object_or_404(AttendanceSession, pk=pk)

    records = AttendanceRecord.objects.filter(
        session=session
    ).select_related('student').order_by('student__name')

    if request.method == "POST":

        for record in records:
            status = request.POST.get(f'status_{record.student.id}')

            if status:
                record.status = status
                record.save()

        messages.success(request, "Attendance updated successfully.")

        return redirect('attendance_session_detail', pk=session.pk)

    return render(request, 'attendance/edit_attendance.html', {
        'session': session,
        'records': records
    })