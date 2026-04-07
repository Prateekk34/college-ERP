from django.db import models
from django.conf import settings


class Faculty(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='faculty_profile',
        null=True,
        blank=True
    )

    name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    # TEMP: keep as text because old data is like "cse"
    department = models.CharField(max_length=100, blank=True, null=True)

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='faculty_members'
    )

    designation = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(upload_to='faculty/', blank=True, null=True)
    date_joined = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name or "Faculty"