from django.urls import path
from . import views

urlpatterns = [
    path('', views.faculty_list, name='faculty_list'),
    path('add/', views.faculty_add, name='faculty_add'),
    path('edit/<int:pk>/', views.faculty_edit, name='faculty_edit'),
    path('delete/<int:pk>/', views.faculty_delete, name='faculty_delete'),
    path('assignments/', views.faculty_assignments, name='faculty_assignments'),
    path('assignments/add/', views.add_assignment, name='add_assignment'),
    path('assignments/<int:pk>/submissions/', views.view_submissions, name='view_submissions'),
    path('submissions/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
    path('profile/edit/', views.faculty_profile_edit, name='faculty_profile_edit'),
]
