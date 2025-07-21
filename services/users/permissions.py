from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission class to allow access only to admin users.
    """
    message = "You must be an admin to perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.has_role('admin')
        )


class IsManagerUser(permissions.BasePermission):
    """
    Permission class to allow access to manager and admin users.
    """
    message = "You must be a manager or admin to perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.has_role('manager') or request.user.has_role('admin'))
        )


class IsEmployeeUser(permissions.BasePermission):
    """
    Permission class to allow access to employee, manager, and admin users.
    """
    message = "You must be authenticated to perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.has_role('employee') or request.user.has_role('manager') or request.user.has_role('admin'))
        )


class IsOwnerOrManagerOrAdmin(permissions.BasePermission):
    """
    Permission class to allow access to the owner of the object, managers, or admins.
    """
    message = "You can only access your own data unless you are a manager or admin."
    
    def has_object_permission(self, request, view, obj):
        # Admin and manager users have full access
        if request.user.has_role('admin') or request.user.has_role('manager'):
            return True
        
        # Check if the object belongs to the user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        else:
            # If no ownership field, check if it's the user object itself
            return obj == request.user


class IsTeamMemberOrManagerOrAdmin(permissions.BasePermission):
    """
    Permission class for team-related access.
    """
    message = "You must be a team member, manager, or admin to access this resource."
    
    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.has_role('admin'):
            return True
        
        # Manager users have access to teams they manage
        if request.user.has_role('manager'):
            if hasattr(obj, 'manager') and obj.manager == request.user:
                return True
            if hasattr(obj, 'team') and hasattr(obj.team, 'manager') and obj.team.manager == request.user:
                return True
        
        # Team members have access to their team's resources
        if hasattr(obj, 'team'):
            return obj.team.members.filter(id=request.user.id).exists()
        elif hasattr(obj, 'members'):
            return obj.members.filter(id=request.user.id).exists()
        
        return False


class RoleBasedPermission(permissions.BasePermission):
    """
    Dynamic permission class based on user roles and action.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin users have full access
        if request.user.has_role('admin'):
            return True
        
        action = getattr(view, 'action', None)
        
        # Define role-based permissions for different actions
        role_permissions = {
            'list': ['admin', 'manager', 'employee'],
            'retrieve': ['admin', 'manager', 'employee'],
            'create': ['admin', 'manager'],
            'update': ['admin', 'manager'],
            'partial_update': ['admin', 'manager'],
            'destroy': ['admin'],
        }
        
        allowed_roles = role_permissions.get(action, [])
        
        # Check if user has any of the allowed roles
        return request.user.role in allowed_roles
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin users have full access
        if request.user.has_role('admin'):
            return True
        
        action = getattr(view, 'action', None)
        
        # For employees, they can only access their own data
        if request.user.has_role('employee') and not request.user.has_role('manager'):
            if action in ['retrieve', 'update', 'partial_update']:
                # Check various ownership patterns
                if hasattr(obj, 'user'):
                    return obj.user == request.user
                elif hasattr(obj, 'created_by'):
                    return obj.created_by == request.user
                elif hasattr(obj, 'assigned_to'):
                    return obj.assigned_to == request.user
                else:
                    return obj == request.user
        
        # Managers can access their team members' data
        if request.user.has_role('manager'):
            if hasattr(obj, 'user'):
                # Check if the user is managed by the current user
                return (
                    obj.user == request.user or
                    (hasattr(obj.user, 'profile') and obj.user.profile.manager == request.user)
                )
            elif hasattr(obj, 'team'):
                return obj.team.manager == request.user
        
        return True


class ReadOnlyOrManagerOrAdmin(permissions.BasePermission):
    """
    Permission class that allows read-only access to all authenticated users,
    but write access only to managers and admins.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Read permissions for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for managers and admins
        return request.user.has_role('manager') or request.user.has_role('admin')


class CustomModelPermission(permissions.DjangoModelPermissions):
    """
    Custom model permission that integrates with our role system.
    """
    
    def has_permission(self, request, view):
        # First check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin users bypass all permission checks
        if request.user.has_role('admin'):
            return True
        
        # Use Django's default model permissions as base
        return super().has_permission(request, view)
    
    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.has_role('admin'):
            return True
        
        # Apply ownership-based permissions for non-admin users
        return super().has_object_permission(request, view, obj)
