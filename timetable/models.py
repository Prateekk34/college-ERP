from django.db import models
from subjects.models import SubjectAssignment


class Timetable(models.Model):
    DAY_CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    )

    subject_assignment = models.ForeignKey(
        SubjectAssignment,
        on_delete=models.CASCADE,
        related_name='timetables'
    )

    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    lecture_number = models.PositiveIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['day', 'lecture_number']
        unique_together = ('subject_assignment', 'day', 'lecture_number')

    def __str__(self):
        return f"{self.subject_assignment} - {self.day} - Lecture {self.lecture_number}"