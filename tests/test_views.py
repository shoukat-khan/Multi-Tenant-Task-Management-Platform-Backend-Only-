"""
Test cases for authentication views and API endpoints.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from Services.users.models import UserProfile, Role
from tests.factories import UserFactory, UserProfileFactory, AdminUserFactory, ManagerUserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistrationView:
    """Test cases for the user registration API endpoint."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = APIClient()
        self.registration_url = reverse('authentication:register')
    
    def test_successful_registration(self):
        """Test successful user registration."""
        data = {
            'email': 'newuser@example.com',
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
        
        response = self.client.post(self.registration_url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'profile' in response.data
        assert response.data['user']['email'] == 'newuser@example.com'
        assert response.data['user']['role'] == Role.EMPLOYEE
        
        # Verify user was created in database
        user = User.objects.get(email='newuser@example.com')
        assert user.role == Role.EMPLOYEE
        assert hasattr(user, 'profile')
    
    def test_registration_with_duplicate_email(self):
        """Test registration with already existing email."""
        UserFactory(email='existing@example.com')
        
        data = {
            'email': 'existing@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
            'role': Role.EMPLOYEE,
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        response = self.client.post(self.registration_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_registration_with_password_mismatch(self):
        """Test registration when passwords don't match."""
        data = {
            'email': 'test@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'DifferentPassword123!',
            'role': Role.EMPLOYEE,
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        response = self.client.post(self.registration_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data
    
    def test_registration_with_weak_password(self):
        """Test registration with weak password."""
        data = {
            'email': 'test@example.com',
            'password': '123',
            'password_confirm': '123',
            'role': Role.EMPLOYEE,
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        response = self.client.post(self.registration_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data
    
    def test_admin_registration(self):
        """Test registering an admin user."""
        data = {
            'email': 'admin@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
            'role': Role.ADMIN,
            'first_name': 'Admin',
            'last_name': 'User'
        }
        
        response = self.client.post(self.registration_url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        user = User.objects.get(email='admin@example.com')
        assert user.role == Role.ADMIN
        assert user.is_staff is True


@pytest.mark.django_db
class TestCustomTokenObtainPairView:
    """Test cases for the login API endpoint."""
    
    def setup_method(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.login_url = reverse('authentication:login')
        self.user = UserFactory(email='test@example.com')
        self.user.set_password('testpass123')
        self.user.save()
    
    def test_successful_login(self):
        """Test successful user login."""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
        assert response.data['user']['email'] == 'test@example.com'
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid password."""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_with_nonexistent_user(self):
        """Test login with non-existent email."""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_with_inactive_user(self):
        """Test login with inactive user account."""
        self.user.is_active = False
        self.user.save()
        
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestLogoutView:
    """Test cases for the logout API endpoint."""
    
    def setup_method(self):
        """Set up test client and authenticated user."""
        self.client = APIClient()
        self.logout_url = reverse('authentication:logout')
        self.user = UserFactory()
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = self.refresh_token.access_token
    
    def test_successful_logout(self):
        """Test successful user logout with token blacklisting."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {'refresh': str(self.refresh_token)}
        response = self.client.post(self.logout_url, data, format='json')
        
        assert response.status_code == status.HTTP_205_RESET_CONTENT
        assert response.data['message'] == 'Successfully logged out'
    
    def test_logout_without_authentication(self):
        """Test logout attempt without authentication."""
        data = {'refresh': str(self.refresh_token)}
        response = self.client.post(self.logout_url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_logout_with_invalid_token(self):
        """Test logout with invalid refresh token."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {'refresh': 'invalid_token'}
        response = self.client.post(self.logout_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserProfileView:
    """Test cases for the user profile API endpoints."""
    
    def setup_method(self):
        """Set up test client and authenticated user."""
        self.client = APIClient()
        self.profile_url = reverse('authentication:profile')
        self.user = UserFactory()
        self.profile = UserProfileFactory(user=self.user)
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = self.refresh_token.access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_get_user_profile(self):
        """Test retrieving user profile."""
        response = self.client.get(self.profile_url)
        
        assert response.status_code == status.HTTP_200_OK
        # Test fields that actually exist on UserProfile model
        assert response.data['phone_number'] == self.profile.phone_number
    
    def test_update_user_profile(self):
        """Test updating user profile."""
        update_data = {
            'phone_number': '+9999999999',
            'address': 'Updated Address'
        }
        
        response = self.client.patch(self.profile_url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['phone_number'] == '+9999999999'
        assert response.data['address'] == 'Updated Address'
        
        # Verify database was updated
        self.profile.refresh_from_db()
        assert self.profile.phone_number == '+9999999999'
    
    def test_profile_access_without_authentication(self):
        """Test accessing profile without authentication."""
        self.client.credentials()  # Remove authentication
        response = self.client.get(self.profile_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRoleBasedPermissions:
    """Test cases for role-based permissions."""
    
    def setup_method(self):
        """Set up test clients for different user roles."""
        self.client = APIClient()
        
        # Create users with different roles
        self.admin = AdminUserFactory()
        self.manager = ManagerUserFactory()
        self.employee = UserFactory()
        
        # Create profiles
        self.admin_profile = UserProfileFactory(user=self.admin)
        self.manager_profile = UserProfileFactory(user=self.manager)
        self.employee_profile = UserProfileFactory(user=self.employee)
    
    def _authenticate_user(self, user):
        """Helper method to authenticate a user."""
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    def test_admin_role_permissions(self):
        """Test that admin users have appropriate permissions."""
        self._authenticate_user(self.admin)
        
        # Admin should be able to access their profile
        profile_url = reverse('authentication:profile')
        response = self.client.get(profile_url)
        assert response.status_code == status.HTTP_200_OK
        
        # Admin should have is_staff = True
        assert self.admin.is_staff is True
        assert self.admin.role == Role.ADMIN
    
    def test_manager_role_permissions(self):
        """Test that manager users have appropriate permissions."""
        self._authenticate_user(self.manager)
        
        # Manager should be able to access their profile
        profile_url = reverse('authentication:profile')
        response = self.client.get(profile_url)
        assert response.status_code == status.HTTP_200_OK
        
        # Manager should not be staff by default
        assert self.manager.is_staff is False
        assert self.manager.role == Role.MANAGER
    
    def test_employee_role_permissions(self):
        """Test that employee users have appropriate permissions."""
        self._authenticate_user(self.employee)
        
        # Employee should be able to access their profile
        profile_url = reverse('authentication:profile')
        response = self.client.get(profile_url)
        assert response.status_code == status.HTTP_200_OK
        
        # Employee should not be staff
        assert self.employee.is_staff is False
        assert self.employee.role == Role.EMPLOYEE
    
    def test_role_hierarchy(self):
        """Test role hierarchy levels using utils module."""
        from Services.authentication.utils import get_role_hierarchy_level
        
        admin_level = get_role_hierarchy_level(Role.ADMIN)
        manager_level = get_role_hierarchy_level(Role.MANAGER)
        employee_level = get_role_hierarchy_level(Role.EMPLOYEE)
        
        assert admin_level > manager_level > employee_level
        assert admin_level == 3
        assert manager_level == 2
        assert employee_level == 1
