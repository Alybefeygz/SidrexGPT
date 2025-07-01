from django.urls import path, include
from profiller.api.views import ProfilViewSet, ProfilDurumViewSet, ProfilFotoUpdateView, create_user_with_profile, update_user, delete_user, toggle_user_active
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from robots.api.views import BrandViewSet

# Ana API Root View
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'robots': 'http://127.0.0.1:8000/api/robots/',
        'profile': reverse('profile-root', request=request, format=format),
        'brands': reverse('brand-list', request=request, format=format),
    })

# Profile API Root View
@api_view(['GET'])
def profile_root(request, format=None):
    return Response({
        'profilleri': reverse('profil-list', request=request, format=format),
        'durum': reverse('durum-list', request=request, format=format),
    })

# Router for profile endpoints
router = DefaultRouter()
router.register(r'profilleri', ProfilViewSet)
router.register(r'durum', ProfilDurumViewSet, basename='durum')

# Ana API router for brands
main_router = DefaultRouter()
main_router.register(r'brands', BrandViewSet, basename='brand')

urlpatterns = [
    # Ana API root
    path('', api_root, name='api-root'),
    
    # Main API endpoints (brands)
    path('', include(main_router.urls)),
    
    # Profile endpoints
    path('profile/', profile_root, name='profile-root'),
    path('profile/', include(router.urls)),
    
    # User creation endpoint
    path('create-user/', create_user_with_profile, name='create-user'),
    
    # User management endpoints
    path('update-user/<int:user_id>/', update_user, name='update-user'),
    path('delete-user/<int:user_id>/', delete_user, name='delete-user'),
    path('toggle-user-active/<int:user_id>/', toggle_user_active, name='toggle-user-active'),
    
    # Diğer endpoints
    path('profil_foto/', ProfilFotoUpdateView.as_view(), name='profil-foto')
]



#? Router ile yorum satırı olarak seçilen satırlar olmadan dilediğimiz işlemi yapabildik