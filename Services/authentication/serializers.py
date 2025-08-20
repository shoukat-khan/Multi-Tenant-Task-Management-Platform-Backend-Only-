from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from Services.users.models import User, UserProfile, Role
from .utils import (
    is_admin_role, is_manager_role, is_employee_role,
    get_role_hierarchy_level, can_manage_user, get_user_role_display,
    is_admin_role_data, is_manager_role_data, is_employee_role_data
)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Password must be at least 8 characters long"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirm your password"
    )
    role = serializers.ChoiceField(choices=Role.choices, required=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'role',
            'password', 'password_confirm'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate(self, attrs):
        """Validate password confirmation."""
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        
        if password != password_confirm:
            raise serializers.ValidationError({'password_confirm': "Passwords do not match."})
        
        # Validate password strength
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        
        return attrs
    
    def create(self, validated_data):
        """Create user with validated data."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        role = validated_data.pop('role', Role.EMPLOYEE)
        
        # Generate username from email
        email = validated_data['email']
        username = email.split('@')[0]
        
        # Ensure username uniqueness
        counter = 1
        original_username = username
        while User.objects.filter(username=username).exists():
            username = f"{original_username}_{counter}"
            counter += 1
        
        user = User(username=username, **validated_data)
        user.role = role
        user.set_password(password)
        
        # Set staff privileges for admin users
        if role == Role.ADMIN:
            user.is_staff = True
        
        user.save()
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes user information.
    Now that User.USERNAME_FIELD = 'email', this works seamlessly.
    """
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user information to response
        user = self.user
        if user is not None:
            data['user'] = {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'full_name': user.get_full_name(),
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'role_display': get_user_role_display(user),
                'is_admin': is_admin_role(user),
                'is_manager': is_manager_role(user),
                'is_employee': is_employee_role(user),
                'hierarchy_level': get_role_hierarchy_level(user),
                'last_login': user.last_login,
            }
        
        return data

    @classmethod  
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['full_name'] = user.get_full_name()
        token['role'] = user.role
        token['role_display'] = get_user_role_display(user)
        token['is_admin'] = is_admin_role(user)
        token['is_manager'] = is_manager_role(user)
        token['hierarchy_level'] = get_role_hierarchy_level(user)
        
        return token


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model with User field updates.
    """
    # Include user fields as writable
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)
    role_display = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'email', 'role', 'role_display',
            'phone_number', 'date_of_birth', 'bio', 'department', 
            'employee_id', 'hire_date', 'timezone', 'address',
            'emergency_contact_name', 'emergency_contact_phone'
        ]
    
    def get_role_display(self, obj):
        """Get role display name."""
        return obj.user.get_role_display()
    
    def update(self, instance, validated_data):
        """Update both UserProfile and User fields."""
        # Extract user data
        user_data = validated_data.pop('user', {})
        
        # Update user fields if provided
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
        
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed user information including profile.
    """
    role_display = serializers.SerializerMethodField()
    role_info = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'role_info', 'last_login', 
            'date_joined', 'profile'
        ]
        read_only_fields = [
            'id', 'username', 'email', 'role', 'role_display', 'role_info',
            'last_login', 'date_joined'
        ]
    
    def get_role_display(self, obj):
        """Get role display name."""
        return obj.get_role_display()
    
    def get_role_info(self, obj):
        """Get detailed role information."""
        return {
            'name': obj.role,
            'display': get_user_role_display(obj),
            'is_admin': is_admin_role(obj),
            'is_manager': is_manager_role(obj),
            'is_employee': is_employee_role(obj),
            'hierarchy_level': get_role_hierarchy_level(obj),
            'can_manage_users': is_admin_role(obj) or is_manager_role(obj),
        }
    
    def get_profile(self, obj):
        """Get user profile information."""
        try:
            profile = obj.profile
            return {
                'bio': profile.bio,
                'department': profile.department,
                'employee_id': profile.employee_id,
                'hire_date': profile.hire_date,
                'manager': {
                    'id': profile.manager.id,
                    'name': profile.manager.get_full_name(),
                    'email': profile.manager.email,
                } if profile.manager else None,
                'timezone': profile.timezone,
                'preferences': profile.preferences,
            }
        except UserProfile.DoesNotExist:
            return None
    
    def update(self, instance, validated_data):
        """Update user instance."""
        # Handle profile picture upload
        if 'profile_picture' in validated_data:
            instance.profile_picture = validated_data['profile_picture']
        
        # Update other fields
        for attr, value in validated_data.items():
            if attr != 'profile_picture':
                setattr(instance, attr, value)
        
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """
    current_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Your current password"
    )
    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Your new password"
    )
    confirm_new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirm your new password"
    )
    
    def validate_current_password(self, value):
        """Validate current password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate new password confirmation."""
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.get('confirm_new_password')
        
        if new_password != confirm_new_password:
            raise serializers.ValidationError("New passwords do not match.")
        
        # Validate password strength
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        
        return attrs


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
        """Get basic role information for list view."""
        return {
            'name': obj.role,
            'display': obj.get_role_display(),
            'hierarchy_level': get_role_hierarchy_level(obj),
        }


class UserAdminDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed user view (admin/manager access).
    """
    role_display = serializers.SerializerMethodField()
    role_info = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    management_info = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'role_info',
            'is_active', 'is_staff', 'last_login', 
            'date_joined', 'profile', 'management_info'
        ]
        read_only_fields = [
            'id', 'username', 'date_joined',
            'last_login', 'role_display', 'role_info', 'management_info'
        ]
    
    def get_role_display(self, obj):
        """Get role display name."""
        return obj.get_role_display()
    
    def get_role_info(self, obj):
        """Get detailed role information."""
        return {
            'name': obj.role,
            'display': get_user_role_display(obj),
            'is_admin': is_admin_role(obj),
            'is_manager': is_manager_role(obj),
            'is_employee': is_employee_role(obj),
            'hierarchy_level': get_role_hierarchy_level(obj),
            'can_manage_users': is_admin_role(obj) or is_manager_role(obj),
        }
    
    def get_management_info(self, obj):
        """Get information about who can manage this user."""
        request = self.context.get('request')
        current_user = request.user if request and hasattr(request, 'user') else None
        
        if not current_user:
            return None
        
        return {
            'can_be_managed_by_current_user': can_manage_user(current_user, obj),
            'is_managed_by_current_user': (
                hasattr(obj, 'profile') and 
                obj.profile.manager == current_user
            ),
            'manager': {
                'id': obj.profile.manager.id,
                'name': obj.profile.manager.get_full_name(),
                'email': obj.profile.manager.email,
            } if hasattr(obj, 'profile') and obj.profile.manager else None,
        }
    
    def get_profile(self, obj):
        """Get detailed user profile."""
        try:
            profile = obj.profile
            return {
                'bio': profile.bio,
                'department': profile.department,
                'employee_id': profile.employee_id,
                'hire_date': profile.hire_date,
                'manager': {
                    'id': profile.manager.id,
                    'name': profile.manager.get_full_name(),
                    'email': profile.manager.email,
                } if profile.manager else None,
                'timezone': profile.timezone,
                'preferences': profile.preferences,
                'created_at': profile.created_at,
                'updated_at': profile.updated_at,
            }
        except UserProfile.DoesNotExist:
            return None
