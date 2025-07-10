from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
import logging

logger = logging.getLogger(__name__)

@never_cache
@ensure_csrf_cookie
@require_http_methods(["GET"])
def get_csrf_token(request):
    """
    CSRF token'ı client'a gönderir ve cookie'yi set eder.
    Cache'lenmez ve sadece GET metoduna izin verir.
    """
    try:
        # CSRF token'ı response'a ekle
        response = JsonResponse({
            'detail': 'CSRF cookie set successfully',
            'csrf_token': request.META.get('CSRF_COOKIE'),
            'secure': request.is_secure(),
            'domain': request.get_host(),
            'success': True
        })
        
        # Debug bilgisi (sadece development'ta)
        from django.conf import settings
        if settings.DEBUG:
            logger.info(f"CSRF token requested from {request.get_host()}")
            logger.info(f"Request secure: {request.is_secure()}")
            logger.info(f"User agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}")
        
        return response
    except Exception as e:
        logger.error(f"CSRF token error: {e}")
        return JsonResponse({
            'error': 'CSRF token could not be set',
            'success': False
        }, status=500) 