from django.urls import path
from . import views

urlpatterns = [
    path('', views.exam_list, name='exam_list'),
    path('add/', views.exam_add, name='exam_add'),
    path('edit/<int:pk>/', views.exam_edit, name='exam_edit'),
    path('delete/<int:pk>/', views.exam_delete, name='exam_delete'),

    path('types/', views.exam_type_list, name='exam_type_list'),
    path('types/add/', views.exam_type_add, name='exam_type_add'),

    path('schedule/', views.exam_schedule_list, name='exam_schedule_list'),
    path('schedule/add/', views.exam_schedule_add, name='exam_schedule_add'),
    path('schedule/edit/<int:pk>/', views.exam_schedule_edit, name='exam_schedule_edit'),
    path('schedule/delete/<int:pk>/', views.exam_schedule_delete, name='exam_schedule_delete'),

    path('my-exams/', views.student_exam_schedule, name='student_exam_schedule'),
    path('faculty-exams/', views.faculty_exam_schedule, name='faculty_exam_schedule'),

    path('results/entry/', views.result_entry, name='result_entry'),
    path('results/list/', views.result_list, name='result_list'),
    path('results/delete/<int:pk>/', views.result_delete, name='result_delete'),
    path('results/student/', views.student_result_list, name='student_result_list'),

    path('marksheet/', views.consolidated_marksheet, name='consolidated_marksheet'),
    path('marksheet/pdf/', views.marksheet_pdf, name='marksheet_pdf'),
]