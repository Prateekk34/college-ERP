from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_list, name='attendance_list'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('session/<int:pk>/', views.attendance_session_detail, name='attendance_session_detail'),
    path('my/', views.my_attendance, name='my_attendance'),
    path('session/<int:pk>/', views.attendance_session_detail, name='attendance_session_detail'),
    path('session/<int:pk>/edit/', views.edit_attendance, name='edit_attendance'),
]