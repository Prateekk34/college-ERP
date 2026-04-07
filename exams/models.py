from django.db import models
from students.models import Student
from subjects.models import SubjectAssignment


class ExamType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Exam(models.Model):
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    semester = models.IntegerField(null=True, blank=True)
    section = models.CharField(max_length=20, blank=True, null=True)

    exam_type = models.ForeignKey(
        ExamType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    title = models.CharField(max_length=200, null=True, blank=True)
    total_marks = models.IntegerField(default=100, null=True, blank=True)

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    exam_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title or f"Exam {self.id}"


class ExamSchedule(models.Model):
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    subject_assignment = models.ForeignKey(
        SubjectAssignment,
        on_delete=models.CASCADE,
        related_name='exam_schedules'
    )
    paper_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True, null=True)
    max_marks = models.IntegerField(default=100)

    class Meta:
        ordering = ['paper_date', 'start_time']
        unique_together = ('exam', 'subject_assignment')

    def __str__(self):
        return f"{self.exam} - {self.subject_assignment.subject.name}"


class Result(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='results'
    )
    subject_assignment = models.ForeignKey(
        SubjectAssignment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='results'
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='results'
    )
    marks_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    remarks = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['student__name']
        unique_together = ('student', 'subject_assignment', 'exam')

    def __str__(self):
        subject_name = self.subject_assignment.subject.name if self.subject_assignment else "-"
        return f"{self.student} - {subject_name} - {self.marks_obtained}"

    @property
    def percentage(self):
        if self.exam and self.exam.total_marks and self.marks_obtained is not None:
            return round((float(self.marks_obtained) / float(self.exam.total_marks)) * 100, 2)
        return 0

    @property
    def grade(self):
        p = self.percentage
        if p >= 90:
            return "A+"
        elif p >= 80:
            return "A"
        elif p >= 70:
            return "B+"
        elif p >= 60:
            return "B"
        elif p >= 50:
            return "C"
        elif p >= 40:
            return "D"
        return "F"