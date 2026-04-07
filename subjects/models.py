from django.db import models
from departments.models import Department
from courses.models import Course
from faculty.models import Faculty


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name} ({self.code})"


class SubjectAssignment(models.Model):
    SEMESTER_CHOICES = (
        (1, 'Semester 1'),
        (2, 'Semester 2'),
        (3, 'Semester 3'),
        (4, 'Semester 4'),
        (5, 'Semester 5'),
        (6, 'Semester 6'),
        (7, 'Semester 7'),
        (8, 'Semester 8'),
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='subject_assignments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subject_assignments'
    )
    semester = models.PositiveSmallIntegerField(choices=SEMESTER_CHOICES)
    section = models.CharField(max_length=20, blank=True, null=True)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='subject_assignments'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['department__name', 'course__name', 'semester', 'section', 'subject__name']
        unique_together = ('course', 'semester', 'section', 'subject')

    def __str__(self):
        sec = self.section if self.section else "-"
        return f"{self.course} | Sem {self.semester} | Sec {sec} | {self.subject} | {self.faculty}"

    def save(self, *args, **kwargs):
        if self.course and self.department_id != self.course.department_id:
            self.department = self.course.department
        super().save(*args, **kwargs)