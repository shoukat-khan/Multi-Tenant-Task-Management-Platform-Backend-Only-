from rest_framework import serializers
from .models import User, UserProfile


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for user list view (minimal information).
    """
    role_display = serializers.SerializerMethodField()
    role_info = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'get_full_name',
            'role', 'role_display', 'role_info', 'is_active', 
            'date_joined'
        ]
        read_only_fields = ['id', 'get_full_name', 'role_display', 'role_info', 'date_joined']
    
    def get_role_display(self, obj):
        """Get role display name."""
        return obj.get_role_display()
    
    def get_role_info(self, obj):
        """Get role information."""
        role_info = {
            'name': obj.role,
            'display_name': obj.get_role_display(),
            'hierarchy_level': {
                'admin': 3,
                'manager': 2,
                'employee': 1
            }.get(obj.role, 0)
        }
        return role_info 