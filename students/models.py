from django.db import models
from django.conf import settings
from departments.models import Department
from courses.models import Course


class Student(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

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

    YEAR_CHOICES = (
        (1, '1st Year'),
        (2, '2nd Year'),
        (3, '3rd Year'),
        (4, '4th Year'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    name = models.CharField(max_length=150)
    enrollment_number = models.CharField(max_length=50, unique=True)
    roll_number = models.CharField(max_length=50, unique=True, blank=True, null=True)

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='students',
        null=True,
        blank=True
    )

    # OLD TEXT COURSE - keep temporarily
    course = models.CharField(max_length=100, blank=True, null=True)

    # NEW FK COURSE - temporary
    course_fk = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        related_name='student_profiles',
        null=True,
        blank=True
    )

    semester = models.PositiveSmallIntegerField(choices=SEMESTER_CHOICES, default=1)
    year = models.PositiveSmallIntegerField(choices=YEAR_CHOICES, default=1)
    section = models.CharField(max_length=20, blank=True, null=True)

    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    photo = models.ImageField(upload_to='students/', blank=True, null=True)
    admission_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.enrollment_number})"