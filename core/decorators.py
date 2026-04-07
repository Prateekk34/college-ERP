from functools import wraps
from django.shortcuts import render, redirect


def role_required(allowed_roles=None):
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            user_role = getattr(request.user, 'role', None)

            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)

            return render(request, 'core/forbidden.html', status=403)

        return wrapper
    return decorator