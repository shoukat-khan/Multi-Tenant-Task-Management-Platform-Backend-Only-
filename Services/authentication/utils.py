"""
Authentication utility functions for role management and permissions.
"""
from Services.users.models import Role


def is_admin_role(user):
    """Check if user has admin role."""
    return user.has_role('admin')


def is_manager_role(user):
    """Check if user has manager role."""
    return user.has_role('manager')


def is_employee_role(user):
    """Check if user has employee role."""
    return user.has_role('employee')


def get_role_hierarchy_level(user_or_role):
    """
    Get the hierarchy level of the user's role or a role directly.
    
    Args:
        user_or_role: User instance or Role choice value
    
    Returns:
        int: Hierarchy level (3=Admin, 2=Manager, 1=Employee, 0=Unknown)
    """
    role_levels = {
        'admin': 3,
        'manager': 2,
        'employee': 1,
        Role.ADMIN: 3,
        Role.MANAGER: 2,
        Role.EMPLOYEE: 1
    }
    
    # If it's a user object, get the role
    if hasattr(user_or_role, 'role'):
        return role_levels.get(user_or_role.role, 0)
    
    # If it's a role directly
    return role_levels.get(user_or_role, 0)


def can_manage_user(current_user, target_user):
    """Check if current user can manage the target user."""
    if is_admin_role(current_user):
        return True
    
    if is_manager_role(current_user):
        # Managers can manage employees and other managers of lower or equal level
        if is_employee_role(target_user):
            return True
        # Check if target user is managed by current user
        if hasattr(target_user, 'profile') and target_user.profile.manager == current_user:
            return True
    
    return current_user == target_user


def get_user_role_display(user):
    """Get the display name of the user's role with additional context."""
    base_display = user.get_role_display()
    
    # Add additional context based on role
    if is_admin_role(user):
        return f"{base_display} (Full Access)"
    elif is_manager_role(user):
        from Services.users.models import User  # Local import to avoid circular imports
        managed_count = getattr(user, 'managed_employees', User.objects.none()).count()
        return f"{base_display} ({managed_count} managed users)"
    else:
        return f"{base_display} (Standard Access)"


# Role validation functions for data (not user objects)
def is_admin_role_data(role_data):
    """Check if the role data is for an admin role."""
    return role_data == Role.ADMIN


def is_manager_role_data(role_data):
    """Check if the role data is for a manager role."""
    return role_data == Role.MANAGER


def is_employee_role_data(role_data):
    """Check if the role data is for an employee role."""
    return role_data == Role.EMPLOYEE
