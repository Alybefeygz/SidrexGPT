from rest_framework import permissions

class KendiProfiliYaDaReadOnly(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        # Admin kullanıcılar her şeyi yapabilir
        if request.user.is_staff or request.user.is_superuser:
            return True
            
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
        
        
class DurumSahibiYaDaReadOnly(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        # Admin kullanıcılar her şeyi yapabilir
        if request.user.is_staff or request.user.is_superuser:
            return True
            
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user_profil == request.user.profil