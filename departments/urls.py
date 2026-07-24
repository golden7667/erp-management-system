from django.urls import path
from . import views

urlpatterns = [
    # Department CRUD
    path('', views.department_list, name='department_list'),
    path('add/', views.department_add, name='department_add'),
    path('edit/<int:pk>/', views.department_edit, name='department_edit'),
    path('delete/<int:pk>/', views.department_delete, name='department_delete'),

    # Classroom Alerts
    path('alerts/', views.classroom_alert_list, name='classroom_alert_list'),
    path('alerts/add/', views.classroom_alert_add, name='classroom_alert_add'),
    path('alerts/edit/<int:pk>/', views.classroom_alert_edit, name='classroom_alert_edit'),
    path('alerts/delete/<int:pk>/', views.classroom_alert_delete, name='classroom_alert_delete'),
    path('alerts/toggle/<int:pk>/', views.classroom_alert_toggle, name='classroom_alert_toggle'),

    # Timetable / Class Schedule
    path('timetable/', views.timetable_view, name='timetable_view'),
    path('timetable/add/', views.timetable_add, name='timetable_add'),
    path('timetable/edit/<int:pk>/', views.timetable_edit, name='timetable_edit'),
    path('timetable/delete/<int:pk>/', views.timetable_delete, name='timetable_delete'),
]
