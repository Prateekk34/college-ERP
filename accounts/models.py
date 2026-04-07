from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("student", "Student"),
        ("faculty", "Faculty"),
        ("admin", "Admin"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="customuser_set",
        related_query_name="customuser"
    )

    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="customuser_permissions_set",
        related_query_name="customuser_permission"
    )

    def __str__(self):
        return self.username