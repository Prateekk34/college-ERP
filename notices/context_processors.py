from .views import get_visible_notices_for_user


def latest_notices(request):
    if not request.user.is_authenticated:
        return {"latest_notices": []}

    notices = get_visible_notices_for_user(request.user)[:5]
    return {"latest_notices": notices}