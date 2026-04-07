"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import dashboard

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('core.urls')),   # ← this connects core app
    path('', include('accounts.urls')),
    path("students/", include("students.urls")),

    path('faculty/', include('faculty.urls')),
    path('courses/', include('courses.urls')),
    path('subjects/', include('subjects.urls')),
    path('attendance/', include('attendance.urls')),
    path("departments/", include("departments.urls")),
    path('exams/', include('exams.urls')),
    path('finance/', include('finance.urls')),
    path('notes/', include('notes.urls')),
    path('timetable/', include('timetable.urls')),
    path("notices/", include("notices.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


