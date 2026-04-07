from django.db import models
from django.utils import timezone
from departments.models import Department
from courses.models import Course


class Notice(models.Model):
    TARGET_CHOICES = (
        ("all", "All Users"),
        ("students", "Students"),
        ("faculty", "Faculty"),
    )

    title = models.CharField(max_length=200)
    message = models.TextField()

    target = models.CharField(
        max_length=20,
        choices=TARGET_CHOICES,
        default="all"
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    publish_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-publish_date", "-id"]

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False