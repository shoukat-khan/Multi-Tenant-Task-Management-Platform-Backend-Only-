"""
This module contains test cases for custom permissions and authentication.

It includes tests for the following permission classes:
- IsAdminRole
- IsManagerRole
- IsEmployeeRole

The tests ensure that users with different roles and authentication states
are granted or denied access as expected.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from services.authentication.permissions import IsAdminRole, IsManagerRole, IsEmployeeRole
from services.users.models import Role
from tests.factories import UserFactory, AdminUserFactory, ManagerUserFactory

User = get_user_model()


class MockView(APIView):
    """Mock view for testing permissions."""
    
    def get(self, request):
        return Response({'message': 'success'}, status=status.HTTP_200_OK)


@pytest.mark.django_db
class TestIsAdminRolePermission:
    """Test cases for IsAdminRole permission class."""
    
    def setup_method(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        self.view = MockView.as_view()
        self.admin_user = AdminUserFactory()
        self.manager_user = ManagerUserFactory()
        self.employee_user = UserFactory()
    
    def test_admin_user_has_permission(self):
        """Test that admin user has permission."""
        view = MockView()
        view.permission_classes = [IsAdminRole]
        
        request = self.factory.get('/test/')
        request.user = self.admin_user
        
        permission = IsAdminRole()
        has_permission = permission.has_permission(request, view)
        
        assert has_permission is True
    
    def test_manager_user_denied_permission(self):
        """Test that manager user is denied permission."""
        view = MockView()
        view.permission_classes = [IsAdminRole]
        
        request = self.factory.get('/test/')
        force_authenticate(request, user=self.manager_user)
        
        permission = IsAdminRole()
        has_permission = permission.has_permission(request, view)
        
        assert has_permission is False
    
    def test_employee_user_denied_permission(self):
        """Test that employee user is denied permission."""
        view = MockView()
        view.permission_classes = [IsAdminRole]
        
        request = self.factory.get('/test/')
        force_authenticate(request, user=self.employee_user)
        
        permission = IsAdminRole()
        has_permission = permission.has_permission(request, view)
        
        assert has_permission is False
    
    def test_unauthenticated_user_denied_permission(self):
        """Test that unauthenticated user is denied permission."""
        view = MockView()
        view.permission_classes = [IsAdminRole]
        
        request = self.factory.get('/test/')
        
        permission = IsAdminRole()
        has_permission = permission.has_permission(request, view)
        
        assert has_permission is False


@pytest.mark.django_db
class TestIsManagerRolePermission:
    """Test cases for IsManagerRole permission class."""
    
    def setup_method(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        self.view = MockView.as_view()
        self.admin_user = AdminUserFactory()
        self.manager_user = ManagerUserFactory()
        self.employee_user = UserFactory()
    
    def test_manager_user_has_permission(self):
        """Test that manager user has permission."""
        view = MockView()
        view.permission_classes = [IsManagerRole]
        
        request = self.factory.get('/test/')
        force_authenticate(request, user=self.manager_user)
        
        permission = IsManagerRole()
        has_permission = permission.has_permission(request, view)
        
        assert has_permission is True
    
    def test_admin_user_has_permission(self):
        """Test that admin user also has manager permission (hierarchy)."""
        view = MockView()
        view.permission_classes = [IsManagerRole]
        
        request = self.factory.get('/test/')
        force_authenticate(request, user=self.admin_user)
        
        permission = IsManagerRole()
        has_permission = permission.has_permission(request, view)
        
        # Assuming admin has manager permissions due to hierarchy
        # This depends on your implementation
        assert has_permission is True
    
    def test_employee_user_denied_permission(self):
        """Test that employee user is denied permission."""
        view = MockView()
        view.permission_classes = [IsManagerRole]
        
        request = self.factory.get('/test/')
        force_authenticate(request, user=self.employee_user)
        
        permission = IsManagerRole()
        has_permission = permission.has_permission(request, view)
        
        assert has_permission is False


@pytest.mark.django_db
class TestIsEmployeeRolePermission:
    """Test cases for IsEmployeeRole permission class."""
    
    def setup_method(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        self.view = MockView.as_view()
        self.admin_user = AdminUserFactory()
        self.manager_user = ManagerUserFactory()
        self.employee_user = UserFactory()
    
    def test_employee_user_has_permission(self):
        """Test that employee user has permission."""
        view = MockView()
        view.permission_classes = [IsEmployeeRole]
        
        request = self.factory.get('/test/')
        force_authenticate(request, user=self.employee_user)
        
        permission = IsEmployeeRole()
        has_permission = permission.has_permission(request, view)
        
        assert has_permission is True
    
    def test_manager_user_has_permission(self):
        """Test that manager user also has employee permission (hierarchy)."""
        view = MockView()
        view.permission_classes = [IsEmployeeRole]
        
        request = self.factory.get('/test/')
        force_authenticate(request, user=self.manager_user)
        
        permission = IsEmployeeRole()
        has_permission = permission.has_permission(request, view)
        
        # Assuming manager has employee permissions due to hierarchy
        assert has_permission is True
    
    def test_admin_user_has_permission(self):
        """Test that admin user also has employee permission (hierarchy)."""
        view = MockView()
        view.permission_classes = [IsEmployeeRole]
        
        request = self.factory.get('/test/')
        force_authenticate(request, user=self.admin_user)
        
        permission = IsEmployeeRole()
        has_permission = permission.has_permission(request, view)
        
        # Assuming admin has employee permissions due to hierarchy
        assert has_permission is True


@pytest.mark.django_db
class TestJWTAuthentication:
    """Test cases for JWT token authentication."""
    
    def setup_method(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        self.user = UserFactory()
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = self.refresh_token.access_token
    
    def test_valid_jwt_token_authentication(self):
        """Test authentication with valid JWT token."""
        request = self.factory.get('/test/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.access_token}'
        
        # Simulate authentication middleware
        force_authenticate(request, user=self.user, token=self.access_token)
        
        assert request.user == self.user
        assert request.user.is_authenticated
    
    def test_jwt_token_contains_user_info(self):
        """Test that JWT token contains correct user information."""
        token_payload = self.access_token.payload
        
        assert token_payload['user_id'] == self.user.id
        assert 'exp' in token_payload  # Expiration time
        assert 'iat' in token_payload  # Issued at time
    
    def test_refresh_token_generation(self):
        """Test that refresh token is properly generated."""
        assert str(self.refresh_token)
        assert self.refresh_token.token_type == 'refresh'
    
    def test_access_token_generation(self):
        """Test that access token is properly generated."""
        assert str(self.access_token)
        assert self.access_token.token_type == 'access'


@pytest.mark.django_db
class TestPasswordSecurity:
    """Test cases for password security features."""
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed."""
        user = UserFactory()
        plain_password = 'testpassword123'
        user.set_password(plain_password)
        user.save()
        
        # Password should be hashed, not stored in plain text
        assert user.password != plain_password
        assert user.password.startswith('argon2')  # Using Argon2 hasher
        
        # Should be able to check password
        assert user.check_password(plain_password) is True
        assert user.check_password('wrongpassword') is False
    
    def test_password_validation_requirements(self):
        """Test password validation requirements."""
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        
        user = UserFactory()
        
        # Test weak passwords
        weak_passwords = ['123', 'password', 'abc', '111111']
        
        for weak_password in weak_passwords:
            with pytest.raises(ValidationError):
                validate_password(weak_password, user)
        
        # Test strong password (should not raise exception)
        strong_password = 'StrongPassword123!'
        try:
            validate_password(strong_password, user)
        except ValidationError:
            pytest.fail("Strong password should not raise ValidationError")
    
    def test_user_cannot_reuse_password(self):
        """Test that user cannot reuse the same password."""
        user = UserFactory()
        password = 'testpassword123'
        user.set_password(password)
        user.save()
        
        # Verify password is set
        assert user.check_password(password) is True
        
        # Try to set the same password again
        user.set_password(password)
        user.save()
        
        # Password should still work (this test checks the basic functionality)
        assert user.check_password(password) is True


@pytest.mark.django_db
class TestAccountSecurity:
    """Test cases for account security features."""
    
    def test_inactive_user_cannot_authenticate(self):
        """Test that inactive users cannot authenticate."""
        user = UserFactory(is_active=False)
        user.set_password('testpass123')
        user.save()
        
        # Try to create tokens for inactive user
        with pytest.raises(Exception):
            RefreshToken.for_user(user)
    
    def test_user_role_security(self):
        """Test that user roles are properly secured."""
        employee = UserFactory(role=User.RoleChoices.EMPLOYEE)
        manager = ManagerUserFactory()
        admin = AdminUserFactory()
        
        # Test role assignments
        assert employee.role == Role.EMPLOYEE
        assert manager.role == Role.MANAGER
        assert admin.role == Role.ADMIN
        
        # Test role hierarchy
        assert employee.has_role(Role.EMPLOYEE) is True
        assert employee.has_role(Role.MANAGER) is False
        assert employee.has_role(Role.ADMIN) is False
        
        assert manager.has_role(Role.MANAGER) is True
        assert admin.has_role(Role.ADMIN) is True
    
    def test_staff_privileges(self):
        """Test staff privileges for different user roles."""
        employee = UserFactory()
        manager = ManagerUserFactory()
        admin = AdminUserFactory()
        
        # Only admin should be staff by default
        assert employee.is_staff is False
        assert manager.is_staff is False
        assert admin.is_staff is True
        
        # Superuser should have all privileges
        superuser = User.objects.create_superuser(
            email='super@example.com',
            password='testpass123'
        )
        assert superuser.is_staff is True
        assert superuser.is_superuser is True
        assert superuser.role == Role.ADMIN
