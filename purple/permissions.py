from rest_framework.permissions import BasePermission

class HasPermissionForAction(BasePermission):
    """
    Custom permission to check if a user has the required permission or is an admin.
    """
    def has_permission(self, request, view):
        user = request.user
        required_permission = getattr(view, 'required_permission', None)
        
        # Grant permission if the user is an admin (is_staff=True)
        if user.is_staff:
            return True
        
        # For sub-admin, check specific permissions
        if user.is_authenticated and required_permission:
            return user.permissions.get(required_permission, False)
        
        return False


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser
