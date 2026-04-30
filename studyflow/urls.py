"""
URLs principales de StudyFlow
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def api_root(request):
    """Page d'accueil de l'API"""
    return JsonResponse({
        "application": "StudyFlow API",
        "version": "1.0",
        "status": "online",
        "documentation": "/api/docs/",
        "endpoints": {
            "admin": "/admin/",
            "auth": "/api/v1/auth/",
            "tasks": "/api/v1/tasks/",
            "collaboration": "/api/v1/collaboration/",
            "progress": "/api/v1/progress/",
        }
    })


urlpatterns = [
    # Page d'accueil API
    path('', api_root, name='api-root'),
    
    # Admin Django
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/tasks/', include('apps.tasks.urls')),
    path('api/v1/collaboration/', include('apps.collaboration.urls')),
    path('api/v1/progress/', include('apps.progress.urls')),

    # API Documentation (Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)