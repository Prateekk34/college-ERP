from django.db import models
from departments.models import Department
from courses.models import Course
from subjects.models import Subject
from faculty.models import Faculty
from students.models import Student


class AttendanceSession(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='attendance_sessions'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='attendance_sessions'
    )
    semester = models.PositiveSmallIntegerField()
    section = models.CharField(max_length=20, blank=True, null=True)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='attendance_sessions'
    )
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_sessions'
    )
    date = models.DateField()
    lecture_number = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'lecture_number']
        unique_together = (
            'department',
            'course',
            'semester',
            'section',
            'subject',
            'date',
            'lecture_number',
        )

    def __str__(self):
        section_text = self.section if self.section else "-"
        return f"{self.course} | Sem {self.semester} | Sec {section_text} | {self.subject} | {self.date} | Lec {self.lecture_number}"

    def total_students(self):
        return self.records.count()

    def present_count(self):
        return self.records.filter(status='Present').count()

    def absent_count(self):
        return self.records.filter(status='Absent').count()

    def leave_count(self):
        return self.records.filter(status='Leave').count()


class AttendanceRecord(models.Model):
    STATUS_CHOICES = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Leave', 'Leave'),
    )

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name='records'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Present')
    remarks = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['student__name']
        unique_together = ('session', 'student')

    def __str__(self):
        return f"{self.student.name} - {self.subject_name()} - {self.status}"

    def subject_name(self):
        return self.session.subject.name if hasattr(self.session.subject, 'name') else str(self.session.subject)