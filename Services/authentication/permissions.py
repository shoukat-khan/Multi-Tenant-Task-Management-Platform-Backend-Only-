"""
Custom permission classes for role-based access control.
"""
from rest_framework import permissions
from Services.users.models import Role



"""
in the file classes 
like IsAdminRole, IsManagerRole, IsEmployeeRole, etc.
These classes define permissions based on user roles.   
THE NEED FOR THE CLASSES IS BECAUSE THEY PROVIDE A WAY TO
restrict access to certain views or actions based on the user's role.

THE FUNCTIONALITY OF THE CLASSES IS TO CHECK IF THE USER HAS
the required role to access a specific view or perform an action.
the function has 3 parameters: 
request, view, and obj.
        return obj.created_by == request.user
"""

class IsAdminRole(permissions.BasePermission):
    """
    Permission class that allows access only to users with Admin role.
    """
    
    def has_permission(self, request, view):
        """Check if user has admin role permission."""
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_role(Role.ADMIN)


class IsManagerRole(permissions.BasePermission):
    """
    Permission class that allows access to users with Manager role or higher.
    Includes Admin users due to role hierarchy.
    """
    
    def has_permission(self, request, view):
        """Check if user has manager role permission or higher."""
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_role(Role.MANAGER) or request.user.has_role(Role.ADMIN)


class IsEmployeeRole(permissions.BasePermission):
    """
    Permission class that allows access to any authenticated user.
    All roles (Employee, Manager, Admin) have employee-level access.
    """
    
    def has_permission(self, request, view):
        """Check if user has employee role permission or higher."""
        if not request.user or not request.user.is_authenticated:
            return False
        return (
            request.user.has_role(Role.EMPLOYEE) or 
            request.user.has_role(Role.MANAGER) or 
            request.user.has_role(Role.ADMIN)
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user is the owner of the object."""
        # Read permissions for any request,
        # Write permissions only to the owner.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Instance must have an attribute named 'user' or 'owner'
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False


class IsAdminOrOwner(permissions.BasePermission):
    """
    Permission class that allows access to admins or object owners.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user is admin or owner of the object."""
        if request.user.has_role(Role.ADMIN):
            return True
        
        # Check if user is the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False


class IsManagerOrOwner(permissions.BasePermission):
    """
    Permission class that allows access to managers, admins, or object owners.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user is manager/admin or owner of the object."""
        if (request.user.has_role(Role.MANAGER) or 
            request.user.has_role(Role.ADMIN)):
            return True
        
        # Check if user is the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False
