from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from students.models import Student
from subjects.models import SubjectAssignment
from faculty.models import Faculty

from .forms import ExamTypeForm, ExamForm, ExamScheduleForm
from .models import ExamType, Exam, ExamSchedule, Result


def is_faculty(user):
    return getattr(user, 'role', None) == 'faculty'


def is_student(user):
    return getattr(user, 'role', None) == 'student'


@login_required
def exam_type_list(request):
    types = ExamType.objects.all().order_by('name')
    return render(request, 'exams/exam_type_list.html', {'types': types})


@login_required
def exam_type_add(request):
    if request.method == 'POST':
        form = ExamTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam type added successfully.")
            return redirect('exam_type_list')
    else:
        form = ExamTypeForm()
    return render(request, 'exams/exam_type_form.html', {'form': form})


@login_required
def exam_list(request):
    exams = Exam.objects.select_related(
        'department', 'course', 'exam_type'
    ).all().order_by('-id')

    return render(request, 'exams/exam_list.html', {
        'exams': exams
    })


@login_required
def exam_add(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam added successfully.")
            return redirect('exam_list')
    else:
        form = ExamForm()

    return render(request, 'exams/exam_form.html', {'form': form})


@login_required
def exam_edit(request, pk):
    exam = get_object_or_404(Exam, pk=pk)

    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam updated successfully.")
            return redirect('exam_list')
    else:
        form = ExamForm(instance=exam)

    return render(request, 'exams/exam_form.html', {
        'form': form,
        'is_edit': True
    })


@login_required
def exam_delete(request, pk):
    exam = get_object_or_404(Exam, pk=pk)

    if request.method == 'POST':
        exam.delete()
        messages.success(request, "Exam deleted successfully.")
        return redirect('exam_list')

    return render(request, 'exams/exam_delete.html', {'exam': exam})


@login_required
def exam_schedule_list(request):
    schedules = ExamSchedule.objects.select_related(
        'exam',
        'subject_assignment',
        'subject_assignment__subject',
        'subject_assignment__course',
        'subject_assignment__department',
        'subject_assignment__faculty',
    ).all()

    return render(request, 'exams/exam_schedule_list.html', {
        'schedules': schedules
    })


@login_required
def exam_schedule_add(request):
    if request.method == 'POST':
        form = ExamScheduleForm(request.POST, faculty_user=request.user if is_faculty(request.user) else None)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam schedule added successfully.")
            return redirect('exam_schedule_list')
    else:
        form = ExamScheduleForm(faculty_user=request.user if is_faculty(request.user) else None)

    return render(request, 'exams/exam_schedule_form.html', {'form': form})


@login_required
def exam_schedule_edit(request, pk):
    schedule = get_object_or_404(ExamSchedule, pk=pk)

    if request.method == 'POST':
        form = ExamScheduleForm(request.POST, instance=schedule, faculty_user=request.user if is_faculty(request.user) else None)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam schedule updated successfully.")
            return redirect('exam_schedule_list')
    else:
        form = ExamScheduleForm(instance=schedule, faculty_user=request.user if is_faculty(request.user) else None)

    return render(request, 'exams/exam_schedule_form.html', {
        'form': form,
        'is_edit': True
    })


@login_required
def exam_schedule_delete(request, pk):
    schedule = get_object_or_404(ExamSchedule, pk=pk)

    if request.method == 'POST':
        schedule.delete()
        messages.success(request, "Exam schedule deleted successfully.")
        return redirect('exam_schedule_list')

    return render(request, 'exams/exam_schedule_delete.html', {'schedule': schedule})


@login_required
def student_exam_schedule(request):
    student = Student.objects.filter(user=request.user).first()

    if not student:
        messages.error(request, "Student profile not found.")
        return redirect('dashboard')

    schedules = ExamSchedule.objects.select_related(
        'exam',
        'subject_assignment',
        'subject_assignment__subject',
        'subject_assignment__faculty',
        'subject_assignment__course',
        'subject_assignment__department',
    ).filter(
        subject_assignment__department=student.department,
        subject_assignment__course=student.course_fk,
        subject_assignment__semester=student.semester,
        exam__is_active=True
    ).order_by('paper_date', 'start_time')

    if student.section:
        schedules = schedules.filter(subject_assignment__section__iexact=student.section)

    return render(request, 'exams/student_exam_schedule.html', {
        'schedules': schedules
    })


@login_required
def faculty_exam_schedule(request):
    faculty = Faculty.objects.filter(user=request.user).first()

    if not faculty:
        messages.error(request, "Faculty profile not linked.")
        return redirect('dashboard')

    schedules = ExamSchedule.objects.select_related(
        'exam',
        'subject_assignment',
        'subject_assignment__subject',
        'subject_assignment__course',
        'subject_assignment__department',
    ).filter(
        subject_assignment__faculty=faculty,
        exam__is_active=True
    ).order_by('paper_date', 'start_time')

    return render(request, 'exams/faculty_exam_schedule.html', {
        'schedules': schedules
    })


@login_required
def result_entry(request):
    faculty_user = request.user if is_faculty(request.user) else None

    exams = Exam.objects.filter(is_active=True).order_by('-id')
    assignments = SubjectAssignment.objects.select_related(
        'subject', 'course', 'department', 'faculty'
    ).filter(is_active=True)

    if faculty_user:
        faculty = Faculty.objects.filter(user=faculty_user).first()
        if faculty:
            assignments = assignments.filter(faculty=faculty)

    students = None
    selected_exam = None
    selected_assignment = None
    existing_results = {}

    if request.method == 'POST':
        exam_id = request.POST.get('exam')
        assignment_id = request.POST.get('subject_assignment')

        if exam_id and assignment_id:
            selected_exam = get_object_or_404(Exam, id=exam_id)
            selected_assignment = get_object_or_404(SubjectAssignment, id=assignment_id)

            students = Student.objects.filter(
                department=selected_assignment.department,
                course_fk=selected_assignment.course,
                semester=selected_assignment.semester
            ).order_by('name')

            if selected_assignment.section:
                students = students.filter(section__iexact=selected_assignment.section)

            previous_results = Result.objects.filter(
                exam=selected_exam,
                subject_assignment=selected_assignment,
                student__in=students
            )

            existing_results = {item.student_id: item for item in previous_results}

            if 'save_results' in request.POST:
                for student in students:
                    marks = request.POST.get(f'marks_{student.id}', '').strip()
                    remarks = request.POST.get(f'remarks_{student.id}', '').strip()

                    if marks != '':
                        Result.objects.update_or_create(
                            student=student,
                            subject_assignment=selected_assignment,
                            exam=selected_exam,
                            defaults={
                                'marks_obtained': marks,
                                'remarks': remarks
                            }
                        )

                messages.success(request, "Results saved successfully.")
                return redirect('result_list')

    return render(request, 'exams/result_entry.html', {
        'exams': exams,
        'assignments': assignments,
        'students': students,
        'selected_exam': selected_exam,
        'selected_assignment': selected_assignment,
        'existing_results': existing_results,
    })


@login_required
def result_list(request):
    query = request.GET.get('q', '')

    results = Result.objects.select_related(
        'student',
        'exam',
        'subject_assignment',
        'subject_assignment__subject'
    ).all()

    if query:
        results = results.filter(
            Q(student__name__icontains=query) |
            Q(student__enrollment_number__icontains=query) |
            Q(subject_assignment__subject__name__icontains=query) |
            Q(exam__title__icontains=query)
        )

    results = results.order_by('-exam__id', 'student__name')

    return render(request, 'exams/result_list.html', {
        'results': results,
        'query': query
    })


@login_required
def result_delete(request, pk):
    result = get_object_or_404(Result, pk=pk)

    if request.method == 'POST':
        result.delete()
        messages.success(request, "Result deleted successfully.")
        return redirect('result_list')

    return render(request, 'exams/result_delete.html', {'result': result})


@login_required
def student_result_list(request):
    student = Student.objects.filter(user=request.user).first()

    if not student:
        messages.error(request, "Student profile not found.")
        return redirect('dashboard')

    results = Result.objects.select_related(
        'student',
        'exam',
        'subject_assignment',
        'subject_assignment__subject'
    ).filter(
        student=student
    ).order_by('exam__title', 'subject_assignment__subject__name')

    return render(request, 'exams/student_result_list.html', {
        'results': results
    })


@login_required
def consolidated_marksheet(request):
    student = Student.objects.filter(user=request.user).first()

    if not student:
        messages.error(request, "Student profile not found.")
        return redirect('dashboard')

    results = Result.objects.select_related(
        'exam',
        'subject_assignment',
        'subject_assignment__subject'
    ).filter(
        student=student
    ).order_by('subject_assignment__subject__name', 'exam__title')

    grouped = {}
    for item in results:
        subject_name = item.subject_assignment.subject.name if item.subject_assignment else '-'
        if subject_name not in grouped:
            grouped[subject_name] = []
        grouped[subject_name].append(item)

    return render(request, 'exams/consolidated_marksheet.html', {
        'student': student,
        'grouped': grouped
    })


@login_required
def marksheet_pdf(request):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    student = Student.objects.filter(user=request.user).first()

    if not student:
        messages.error(request, "Student profile not found.")
        return redirect('dashboard')

    results = Result.objects.select_related(
        'exam',
        'subject_assignment',
        'subject_assignment__subject'
    ).filter(student=student).order_by('subject_assignment__subject__name', 'exam__title')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="marksheet.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 50
    p.setFont("Helvetica-Bold", 16)
    p.drawString(180, y, "College ERP Marksheet")

    y -= 30
    p.setFont("Helvetica", 11)
    p.drawString(50, y, f"Student Name: {student.name}")
    y -= 20
    p.drawString(50, y, f"Enrollment No: {student.enrollment_number}")
    y -= 20
    p.drawString(50, y, f"Course: {student.course_fk}")
    y -= 20
    p.drawString(50, y, f"Semester: {student.semester}")

    y -= 35
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Subject")
    p.drawString(220, y, "Exam")
    p.drawString(340, y, "Marks")
    p.drawString(420, y, "Percentage")
    p.drawString(500, y, "Grade")

    y -= 20
    p.setFont("Helvetica", 10)

    for item in results:
        if y < 50:
            p.showPage()
            y = height - 50

        subject_name = item.subject_assignment.subject.name if item.subject_assignment else '-'
        p.drawString(50, y, str(subject_name)[:25])
        p.drawString(220, y, str(item.exam.title)[:18])
        p.drawString(340, y, f"{item.marks_obtained}/{item.exam.total_marks}")
        p.drawString(420, y, f"{item.percentage}%")
        p.drawString(500, y, item.grade)
        y -= 18

    p.save()
    return response