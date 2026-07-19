from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('add/', views.student_add, name='student_add'),
    path('edit/<int:pk>/', views.student_edit, name='student_edit'),
    path('delete/<int:pk>/', views.student_delete, name='student_delete'),
    path('id-card/<int:pk>/', views.student_id_card, name='student_id_card'),
    path('assignments/', views.student_assignments, name='student_assignments'),
    path('assignments/<int:pk>/submit/', views.submit_assignment, name='submit_assignment'),
    path('profile/edit/', views.student_profile_edit, name='student_profile_edit'),
]
