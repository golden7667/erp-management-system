from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify/<str:uidb64>/<str:token>/', views.verify_email_view, name='verify_email'),
    path('reset/<str:uidb64>/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    
    # JWT API routes
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Role‑specific login URLs
    path('student/login/', views.student_login_view, name='student_login'),
    path('faculty/login/', views.faculty_login_view, name='faculty_login'),
    path('admin/login/', views.admin_login_view, name='admin_login'),

    # Admin password change for any user
    path('admin/change-password/<int:user_id>/', views.admin_change_user_password, name='admin_change_user_password'),

]
