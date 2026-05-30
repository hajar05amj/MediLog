from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse
import os, socket, json
from users.views import SeedView
from reservations.views import OrdonnanceView, PatientOrdonnanceListView

def get_server_ip(request):
    """Returns the server's local network IP for QR code generation."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        ip = '127.0.0.1'
    return JsonResponse({'ip': ip, 'port': request.META.get('SERVER_PORT', '8000')})

def serve_frontend(request, filename='index.html'):
    frontend_dir = os.path.join(settings.BASE_DIR, 'frontend')
    file_path = os.path.join(frontend_dir, filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            content = f.read()
        content_type = 'text/html'
        if filename.endswith('.css'):
            content_type = 'text/css'
        elif filename.endswith('.js'):
            content_type = 'application/javascript'
        elif filename.endswith('.json'):
            content_type = 'application/json'
        elif filename.endswith('.png'):
            content_type = 'image/png'
        elif filename.endswith('.ico'):
            content_type = 'image/x-icon'
        elif filename.endswith('.webmanifest'):
            content_type = 'application/manifest+json'
        response = HttpResponse(content, content_type=content_type)
        # Prevent browser caching for HTML and JS files
        if filename.endswith('.html') or filename.endswith('.js'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response
    return HttpResponse('Not found', status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('auth/', include('users.urls')),
    path('users/', include('users.urls')),
    path('reservations/', include([
        path('', include('reservations.urls')),
        path('', include('tracking.urls')),
    ])),
    path('files/', include('files.urls')),
    path('courier/', include('delivery.urls')),
    path('tracking/', include('tracking.urls')),
    path('seed/', SeedView.as_view()),
    path('server-ip/', get_server_ip),
    
    # Ordonnance APIs
    path('ordonnance/', OrdonnanceView.as_view()),
    path('patient/<int:patient_id>/ordonnances/', PatientOrdonnanceListView.as_view()),
    
    
    # Serve frontend files
    path('', lambda req: serve_frontend(req, 'index.html')),
    path('<path:filename>', serve_frontend),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
