"""
URL configuration for dashboard project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard.views import WebSocketView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ws', WebSocketView.as_view(), name='websocket'),
    path('', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)