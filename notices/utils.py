from django.utils import timezone
from .models import Notice


def get_dashboard_notices(user):

    notices = Notice.objects.filter(
        is_active=True,
        publish_date__lte=timezone.now()
    )

    if user.is_superuser:
        return notices[:5]

    role = getattr(user, "role", None)

    if role == "student":
        notices = notices.filter(target__in=["all", "students"])

    elif role == "faculty":
        notices = notices.filter(target__in=["all", "faculty"])

    return notices[:5]