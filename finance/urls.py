from django.urls import path
from . import views

urlpatterns = [

     path('', views.finance_home, name='finance_home'),
    path('structures/', views.fee_structure_list, name='fee_structure_list'),
    path('structures/add/', views.fee_structure_add, name='fee_structure_add'),
    path('structures/edit/<int:pk>/', views.fee_structure_edit, name='fee_structure_edit'),

    path('students/', views.student_fee_list, name='student_fee_list'),
    path('students/add/', views.student_fee_add, name='student_fee_add'),
    path('students/<int:pk>/', views.student_fee_detail, name='student_fee_detail'),

    path('students/<int:pk>/extra/add/', views.extra_fee_add, name='extra_fee_add'),
    path('students/<int:pk>/installment/add/', views.installment_add, name='installment_add'),

    path('installment/<int:pk>/edit/', views.installment_edit, name='installment_edit'),
    path('installment/<int:pk>/delete/', views.installment_delete, name='installment_delete'),
    path('installment/<int:pk>/receipt/', views.installment_receipt_pdf, name='installment_receipt_pdf'),

    path('promote/', views.promote_student_fee, name='promote_student_fee'),

    path('my-fees/', views.my_fees, name='my_fees'),
]