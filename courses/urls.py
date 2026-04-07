from django.urls import path
from . import views

urlpatterns = [
    path("", views.course_list, name="course_list"),
    path("add/", views.add_course, name="add_course"),
    path("edit/<int:pk>/", views.edit_course, name="edit_course"),
    path("delete/<int:pk>/", views.delete_course, name="delete_course"),
    path("profile/<int:pk>/", views.course_profile, name="course_profile"),
]