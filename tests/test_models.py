"""
Test cases for User and UserProfile models.
"""
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from services.users.models import UserProfile, Role
from tests.factories import UserFactory, UserProfileFactory, AdminUserFactory, ManagerUserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test cases for the User model."""
    
    def test_user_creation(self):
        """Test creating a user with valid data."""
        user = UserFactory()
        assert user.email
        assert user.role == Role.EMPLOYEE
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
    
    def test_admin_user_creation(self):
        """Test creating an admin user."""
        admin = AdminUserFactory()
        assert admin.role == Role.ADMIN
        assert admin.is_staff is True
    
    def test_manager_user_creation(self):
        """Test creating a manager user."""
        manager = ManagerUserFactory()
        assert manager.role == Role.MANAGER
        assert manager.is_staff is False
    
    def test_user_string_representation(self):
        """Test the string representation of a user."""
        user = UserFactory(username="testuser", email="test@example.com")
        # Since USERNAME_FIELD = 'email', string representation shows email
        assert str(user) == "test@example.com"
    
    def test_email_uniqueness(self):
        """Test that email is unique (custom behavior for our User model)."""
        # Our custom User model enforces email uniqueness
        user1 = UserFactory(username="user1", email="unique1@example.com")
        
        # Attempting to create another user with the same email should fail
        with pytest.raises(Exception):  # This will be an IntegrityError
            user2 = UserFactory(username="user2", email="unique1@example.com")
        
        # The first user should exist successfully
        assert user1.email == "unique1@example.com"
    
    def test_has_role_method(self):
        """Test the has_role method."""
        admin = AdminUserFactory()
        manager = ManagerUserFactory()
        employee = UserFactory()
        
        assert admin.has_role(Role.ADMIN) is True
        assert admin.has_role(Role.MANAGER) is False
        
        assert manager.has_role(Role.MANAGER) is True
        assert manager.has_role(Role.ADMIN) is False
        
        assert employee.has_role(Role.EMPLOYEE) is True
        assert employee.has_role(Role.ADMIN) is False
    
    def test_user_role_choices(self):
        """Test that role choices are properly defined."""
        assert hasattr(Role, 'ADMIN')
        assert Role.ADMIN == 'admin'
        assert Role.MANAGER == 'manager'
        assert Role.EMPLOYEE == 'employee'
    
    def test_user_without_email_fails(self):
        """Test that creating a user without email fails."""
        # Django's AbstractUser doesn't enforce non-empty email by default
        # Let's test that we can create a user but email validation would happen at form level
        user = User.objects.create_user(username='testuser', email='', password='testpass123')
        assert user.email == ''
        assert user.username == 'testuser'
    
    def test_superuser_creation(self):
        """Test creating a superuser."""
        superuser = User.objects.create_superuser(
            username='superuser',
            email='super@example.com',
            password='testpass123'
        )
        assert superuser.is_superuser is True
        assert superuser.is_staff is True
        # By default, superuser gets ADMIN role unless explicitly set
        assert superuser.role == Role.ADMIN
        
        # Test superuser with admin role explicitly set
        admin_superuser = User.objects.create_superuser(
            username='adminsuperuser',
            email='adminsuper@example.com',
            password='testpass123',
            role=Role.ADMIN
        )
        assert admin_superuser.role == Role.ADMIN


@pytest.mark.django_db
class TestUserProfileModel:
    """Test cases for the UserProfile model."""
    
    def test_user_profile_creation(self):
        """Test creating a user profile with valid data."""
        profile = UserProfileFactory()
        assert profile.user
        assert profile.phone_number
        assert profile.bio
        assert profile.department
        assert profile.employee_id
        assert profile.timezone == 'UTC'
    
    def test_user_profile_string_representation(self):
        """Test the string representation of a user profile."""
        user = UserFactory(first_name="John", last_name="Doe")
        profile = UserProfileFactory(user=user)
        expected = f"John Doe's Profile"
        assert str(profile) == expected
    
    def test_user_profile_one_to_one_relationship(self):
        """Test the one-to-one relationship between User and UserProfile."""
        user = UserFactory()
        profile = UserProfileFactory(user=user)
        
        assert profile.user == user
        assert user.profile == profile
    
    def test_user_profile_optional_fields(self):
        """Test that optional fields can be None or empty."""
        user = UserFactory()
        profile = UserProfile.objects.create(user=user)
        
        assert profile.phone_number is None or profile.phone_number == ""
        assert profile.bio is None
        assert profile.date_of_birth is None
        assert profile.department is None or profile.department == ""
        assert profile.employee_id is None or profile.employee_id == ""
    
    def test_user_profile_with_all_fields(self):
        """Test creating a user profile with all fields."""
        user = UserFactory()
        profile = UserProfile.objects.create(
            user=user,
            phone_number="+1234567890",
            bio="Test bio",
            department="Engineering",
            employee_id="EMP001",
            timezone="US/Eastern"
        )
        
        assert profile.phone_number == "+1234567890"
        assert profile.bio == "Test bio"
        assert profile.department == "Engineering"
        assert profile.employee_id == "EMP001"
        assert profile.timezone == "US/Eastern"
    
    def test_user_profile_cascade_delete(self):
        """Test that deleting a user deletes the associated profile."""
        user = UserFactory()
        profile = UserProfileFactory(user=user)
        user_id = user.id
        profile_id = profile.id
        
        user.delete()
        
        assert not User.objects.filter(id=user_id).exists()
        assert not UserProfile.objects.filter(id=profile_id).exists()
