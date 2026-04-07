from django.urls import path
from . import views

urlpatterns = [
    path('', views.faculty_list, name='faculty_list'),
    path('add/', views.add_faculty, name='add_faculty'),
    path('edit/<int:pk>/', views.edit_faculty, name='edit_faculty'),
    path('delete/<int:pk>/', views.delete_faculty, name='delete_faculty'),
    path('profile/<int:pk>/', views.faculty_profile, name='faculty_profile'),
    path('my-profile/', views.my_faculty_profile, name='my_faculty_profile'),
    path('my-subjects/', views.my_assigned_subjects, name='my_assigned_subjects'),
]