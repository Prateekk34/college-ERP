from django.urls import path
from . import views

urlpatterns = [
    path('faculty/', views.faculty_note_list, name='faculty_note_list'),
    path('upload/', views.upload_note, name='upload_note'),
    path('edit/<int:pk>/', views.edit_note, name='edit_note'),
    path('delete/<int:pk>/', views.delete_note, name='delete_note'),
    path('student/', views.student_note_list, name='student_note_list'),
]