from django.urls import path
from . import views

urlpatterns = [
    path('', views.subject_list, name='subject_list'),
    path('add/', views.subject_add, name='subject_add'),
    path('edit/<int:pk>/', views.subject_edit, name='subject_edit'),
    path('delete/<int:pk>/', views.subject_delete, name='subject_delete'),

    path('assignments/', views.subject_assignment_list, name='subject_assignment_list'),
    path('assignments/add/', views.subject_assignment_add, name='subject_assignment_add'),
    path('assignments/edit/<int:pk>/', views.subject_assignment_edit, name='subject_assignment_edit'),
    path('assignments/delete/<int:pk>/', views.subject_assignment_delete, name='subject_assignment_delete'),

    path('my/', views.my_subjects, name='my_subjects'),
]