"""
Test cases for authentication serializers.
"""
import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import ValidationError
from rest_framework import serializers
from Services.authentication.serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer
)
from Services.users.models import UserProfile, Role
from tests.factories import UserFactory, UserProfileFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistrationSerializer:
    """Test cases for the UserRegistrationSerializer."""
    
    def test_valid_registration_data(self):
        """Test serializer with valid registration data."""
        data = {
            'email': 'test@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
            'role': Role.EMPLOYEE,
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '+1234567890',
            'address': '123 Main St',
            'date_of_birth': '1990-01-01',
            'emergency_contact_name': 'Jane Doe',
            'emergency_contact_phone': '+0987654321'
        }
        
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        
        user = serializer.save()
        assert user.email == 'test@example.com'
        assert user.role == Role.EMPLOYEE
        assert user.check_password('StrongPassword123!')
        
        # Check that profile was created
        assert hasattr(user, 'profile')
        # Note: first_name/last_name are on User model, not UserProfile
    
    def test_password_mismatch(self):
        """Test serializer validation when passwords don't match."""
        data = {
            'email': 'test@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'DifferentPassword123!',
            'role': Role.EMPLOYEE,
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password_confirm' in serializer.errors
    
    def test_duplicate_email(self):
        """Test serializer validation with duplicate email."""
        UserFactory(email='existing@example.com')
        
        data = {
            'email': 'existing@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
            'role': Role.EMPLOYEE,
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
    
    def test_weak_password(self):
        """Test serializer validation with weak password."""
        data = {
            'email': 'test@example.com',
            'password': '123',
            'password_confirm': '123',
            'role': Role.EMPLOYEE,
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
    
    def test_role_utility_functions(self):
        """Test role utility functions from utils module."""
        from Services.authentication.utils import is_admin_role_data, is_manager_role_data, is_employee_role_data
        
        # Test role utility functions with role data
        assert is_admin_role_data(Role.ADMIN) is True
        assert is_admin_role_data(Role.MANAGER) is False
        assert is_admin_role_data(Role.EMPLOYEE) is False
        
        assert is_manager_role_data(Role.MANAGER) is True
        assert is_manager_role_data(Role.ADMIN) is False
        assert is_manager_role_data(Role.EMPLOYEE) is False
        
        assert is_employee_role_data(Role.EMPLOYEE) is True
        assert is_employee_role_data(Role.ADMIN) is False
        assert is_employee_role_data(Role.MANAGER) is False
    
    def test_role_hierarchy_levels(self):
        """Test get_role_hierarchy_level function from utils module."""
        from Services.authentication.utils import get_role_hierarchy_level
        
        admin_level = get_role_hierarchy_level(Role.ADMIN)
        manager_level = get_role_hierarchy_level(Role.MANAGER)
        employee_level = get_role_hierarchy_level(Role.EMPLOYEE)
        
        assert admin_level > manager_level > employee_level
        assert admin_level == 3
        assert manager_level == 2
        assert employee_level == 1
    
    def test_admin_role_creation(self):
        """Test creating user with admin role."""
        data = {
            'email': 'admin@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
            'role': Role.ADMIN,
            'first_name': 'Admin',
            'last_name': 'User'
        }
        
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        
        user = serializer.save()
        assert user.role == Role.ADMIN
        assert user.is_staff is True  # Admin should be staff


@pytest.mark.django_db
class TestCustomTokenObtainPairSerializer:
    """Test cases for the CustomTokenObtainPairSerializer."""
    
    def test_valid_login_credentials(self):
        """Test serializer with valid login credentials."""
        user = UserFactory(email='test@example.com')
        user.set_password('testpass123')
        user.save()
        
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        serializer = CustomTokenObtainPairSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        
        token_data = serializer.validated_data
        assert 'access' in token_data
        assert 'refresh' in token_data
    
    def test_invalid_credentials(self):
        """Test serializer with invalid credentials."""
        user = UserFactory(email='test@example.com')
        user.set_password('correctpass')
        user.save()
        
        data = {
            'email': 'test@example.com',
            'password': 'wrongpass'
        }
        
        serializer = CustomTokenObtainPairSerializer(data=data)
        # JWT serializers raise AuthenticationFailed exception for invalid credentials
        with pytest.raises(AuthenticationFailed):
            serializer.is_valid(raise_exception=True)
    
    def test_inactive_user_login(self):
        """Test login attempt with inactive user."""
        user = UserFactory(email='test@example.com', is_active=False)
        user.set_password('testpass123')
        user.save()
        
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        serializer = CustomTokenObtainPairSerializer(data=data)
        # JWT serializers raise AuthenticationFailed exception for inactive users
        with pytest.raises(AuthenticationFailed):
            serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
class TestUserProfileSerializer:
    """Test cases for the UserProfileSerializer."""
    
    def test_valid_profile_data(self):
        """Test serializer with valid profile data."""
        user = UserFactory()
        profile = UserProfileFactory(user=user)
        
        serializer = UserProfileSerializer(profile)
        data = serializer.data
        
        # Test fields that actually exist on UserProfile model
        assert data['phone_number'] == profile.phone_number
        assert data['address'] == profile.address
        assert data['emergency_contact_name'] == profile.emergency_contact_name
        assert data['emergency_contact_phone'] == profile.emergency_contact_phone
    
    def test_profile_update(self):
        """Test updating profile data through serializer."""
        user = UserFactory()
        profile = UserProfileFactory(user=user)
        
        update_data = {
            'phone_number': '+9999999999',
            'address': 'Updated Address'
        }
        
        serializer = UserProfileSerializer(profile, data=update_data, partial=True)
        assert serializer.is_valid(), serializer.errors
        
        updated_profile = serializer.save()
        assert updated_profile.phone_number == '+9999999999'
        assert updated_profile.address == 'Updated Address'
    
    def test_profile_update_with_user_fields(self):
        """Test updating profile with user fields through serializer."""
        user = UserFactory()
        profile = UserProfileFactory(user=user)
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'phone_number': '+1111111111',
            'address': 'New Address'
        }
        
        serializer = UserProfileSerializer(profile, data=update_data, partial=True)
        assert serializer.is_valid(), serializer.errors
        
        updated_profile = serializer.save()
        assert updated_profile.user == user
        assert updated_profile.phone_number == '+1111111111'
        assert updated_profile.address == 'New Address'
        
        # Verify user fields were updated
        user.refresh_from_db()
        assert user.first_name == 'Updated'
        assert user.last_name == 'User'
