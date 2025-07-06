"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import get_csrf_token

def health_check(request):
    """Health check endpoint for Render.com"""
    return JsonResponse({
        'status': 'healthy',
        'message': 'SidrexGPT Backend is running successfully!',
        'api_endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'auth': '/api/rest-auth/',
            'profiles': '/api/profile/profilleri/',
            'robots': '/api/robots/',
            'brands': '/api/brands/',
            'robot_pdfs': '/api/robot-pdfs/'
        }
    })

urlpatterns = [
    path('', health_check, name='health_check'),  # Root URL için health check
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),  # Browsable API için
    path('api/rest-auth/', include('dj_rest_auth.urls')),  # Güncellenmiş paket kullanımı
    path('api/rest-auth/registration/', include('dj_rest_auth.registration.urls')),  # Bu satır düzeltildi
    path('api/', include('profiller.api.urls')),
    path('api/', include('robots.api.urls')),  # Brand API'si için ana URL'yi güncelle
    path('api/csrf/', get_csrf_token, name='get_csrf_token'),  # Yeni CSRF endpoint
]

# Canlı (production) ve geliştirme (development) ortamları için 
# statik ve medya dosyalarını sunmak üzere URL desenlerini genişlet.
if settings.DEBUG:
    # Geliştirme ortamında, Django'nun kendi sunucusu medya dosyalarını sunar.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Canlı ortamda, WhiteNoise statik dosyaları sunar.
    # Bu ayar, `collectstatic` ile toplanan dosyaların doğru şekilde bulunmasını sağlar.
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Add this line for serving static files in production
urlpatterns += staticfiles_urlpatterns()
