"""
URL configuration for college_erp project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False), name='home'),
    
    # Modules routing
    path('accounts/', include('accounts.urls')),
    path('students/', include('students.urls')),
    path('faculty/', include('faculty.urls')),
    path('departments/', include('departments.urls')),
    
    # Base/Dashboard route
    path('dashboard/', include('accounts.dashboard_urls')),

    # Authentication URLs (removed)
    # LOGIN_URL = '/accounts/login/'
    # LOGIN_REDIRECT_URL = '/dashboard/'
    # LOGOUT_REDIRECT_URL = '/accounts/login/'
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
