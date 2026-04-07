from django.db import models
from faculty.models import Faculty
from subjects.models import SubjectAssignment


class Note(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    subject_assignment = models.ForeignKey(
        SubjectAssignment,
        on_delete=models.CASCADE,
        related_name='notes'
    )

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_notes'
    )

    file = models.FileField(upload_to='notes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title