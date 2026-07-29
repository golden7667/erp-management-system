"""
URL configuration for college_erp project.
"""
import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.static import serve
from django.http import HttpResponseRedirect

def custom_media_serve(request, path):
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(full_path):
        return serve(request, path, document_root=settings.MEDIA_ROOT)
    # If media file does not exist, redirect to avatar generator so no 404 occurs
    seed = path.replace('/', '_').replace('.', '_')
    return HttpResponseRedirect(f"https://api.dicebear.com/7.x/adventurer/svg?seed={seed}")

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

    # Media files route with automatic avatar fallback
    re_path(r'^media/(?P<path>.*)$', custom_media_serve),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
