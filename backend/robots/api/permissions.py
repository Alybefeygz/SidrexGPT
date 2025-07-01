from rest_framework import permissions
from ..models import Robot, Brand

class CanAccessRobotData(permissions.BasePermission):
    """
    Allows access only to admins or users whose brand matches the robot's brand.
    """
    message = "Bu robota ait verilere erişim izniniz bulunmamaktadır."

    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # The object being accessed must be a Robot instance
        if not isinstance(obj, Robot):
            # This permission is not for this object type, so let other permissions handle it.
            return True 

        # Normal users can access only if the robot belongs to their brand
        if hasattr(request.user, 'profil') and request.user.profil.brand:
            return obj.brand == request.user.profil.brand
        
        return False 

class CanAccessBrandData(permissions.BasePermission):
    """
    Allows access to brand data based on user permissions:
    - Admin users can access and modify all brands
    - Normal users can only view their own brand
    """
    message = "Bu markaya ait verilere erişim izniniz bulunmamaktadır."

    def has_permission(self, request, view):
        # Admin users have full access
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # For list view, check if user has a brand
        if view.action == 'list':
            return hasattr(request.user, 'profil') and request.user.profil.brand is not None
        
        return True

    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Normal users can only access their own brand
        if hasattr(request.user, 'profil') and request.user.profil.brand:
            return obj == request.user.profil.brand
        
        return False 