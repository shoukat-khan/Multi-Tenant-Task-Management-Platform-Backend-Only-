"""
Integration tests for the complete authentication system.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from services.users.models import UserProfile, Role
from tests.factories import UserFactory, UserProfileFactory

User = get_user_model()


@pytest.mark.django_db
class TestAuthenticationFlow:
    """Integration tests for complete authentication flow."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = APIClient()
    
    def test_complete_user_journey(self):
        """Test complete user journey from registration to profile management."""
        # 1. User Registration
        registration_data = {
            'email': 'journey@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
            'role': Role.EMPLOYEE,
            'first_name': 'Journey',
            'last_name': 'User',
            'phone_number': '+1234567890',
            'address': '123 Journey St',
            'date_of_birth': '1990-01-01',
            'emergency_contact_name': 'Emergency Contact',
            'emergency_contact_phone': '+0987654321'
        }
        
        registration_url = reverse('authentication:register')
        registration_response = self.client.post(registration_url, registration_data, format='json')
        
        assert registration_response.status_code == status.HTTP_201_CREATED
        assert registration_response.data['user']['email'] == 'journey@example.com'
        
        # 2. User Login
        login_data = {
            'email': 'journey@example.com',
            'password': 'StrongPassword123!'
        }
        
        login_url = reverse('authentication:login')
        login_response = self.client.post(login_url, login_data, format='json')
        
        assert login_response.status_code == status.HTTP_200_OK
        assert 'access' in login_response.data
        assert 'refresh' in login_response.data
        
        # Extract tokens
        access_token = login_response.data['access']
        refresh_token = login_response.data['refresh']
        
        # 3. Access Protected Profile Endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        profile_url = reverse('authentication:profile')
        profile_response = self.client.get(profile_url)
        
        assert profile_response.status_code == status.HTTP_200_OK
        assert profile_response.data['first_name'] == 'Journey'
        assert profile_response.data['last_name'] == 'User'
        
        # 4. Update Profile
        update_data = {
            'first_name': 'Updated Journey',
            'phone_number': '+9999999999'
        }
        
        update_response = self.client.patch(profile_url, update_data, format='json')
        
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.data['first_name'] == 'Updated Journey'
        assert update_response.data['phone_number'] == '+9999999999'
        
        # 5. Token Refresh
        refresh_url = reverse('authentication:token_refresh')
        refresh_data = {'refresh': refresh_token}
        refresh_response = self.client.post(refresh_url, refresh_data, format='json')
        
        assert refresh_response.status_code == status.HTTP_200_OK
        assert 'access' in refresh_response.data
        
        # Update refresh token if provided in response (some implementations provide new refresh token)
        if 'refresh' in refresh_response.data:
            refresh_token = refresh_response.data['refresh']
        
        # 6. Logout
        logout_url = reverse('authentication:logout')
        logout_data = {'refresh': refresh_token}
        logout_response = self.client.post(logout_url, logout_data, format='json')
        
        assert logout_response.status_code == status.HTTP_205_RESET_CONTENT
        assert logout_response.data['message'] == 'Successfully logged out'
        
        # 7. Clear credentials and verify logout by trying to access protected endpoint
        self.client.credentials()  # Clear authorization header
        profile_after_logout = self.client.get(profile_url)
        assert profile_after_logout.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_admin_user_workflow(self):
        """Test admin user specific workflow."""
        # Register admin user
        admin_data = {
            'email': 'admin@example.com',
            'password': 'AdminPassword123!',
            'password_confirm': 'AdminPassword123!',
            'role': Role.ADMIN,
            'first_name': 'Admin',
            'last_name': 'User'
        }
        
        registration_url = reverse('authentication:register')
        registration_response = self.client.post(registration_url, admin_data, format='json')
        
        assert registration_response.status_code == status.HTTP_201_CREATED
        
        # Verify admin user has staff privileges
        admin_user = User.objects.get(email='admin@example.com')
        assert admin_user.role == Role.ADMIN
        assert admin_user.is_staff is True
        
        # Login and access profile
        login_data = {
            'email': 'admin@example.com',
            'password': 'AdminPassword123!'
        }
        
        login_url = reverse('authentication:login')
        login_response = self.client.post(login_url, login_data, format='json')
        
        assert login_response.status_code == status.HTTP_200_OK
        assert login_response.data['user']['role'] == Role.ADMIN
    
    def test_manager_user_workflow(self):
        """Test manager user specific workflow."""
        # Register manager user
        manager_data = {
            'email': 'manager@example.com',
            'password': 'ManagerPassword123!',
            'password_confirm': 'ManagerPassword123!',
            'role': Role.MANAGER,
            'first_name': 'Manager',
            'last_name': 'User'
        }
        
        registration_url = reverse('authentication:register')
        registration_response = self.client.post(registration_url, manager_data, format='json')
        
        assert registration_response.status_code == status.HTTP_201_CREATED
        
        # Verify manager user
        manager_user = User.objects.get(email='manager@example.com')
        assert manager_user.role == Role.MANAGER
        assert manager_user.is_staff is False  # Manager is not staff by default
        
        # Login and verify
        login_data = {
            'email': 'manager@example.com',
            'password': 'ManagerPassword123!'
        }
        
        login_url = reverse('authentication:login')
        login_response = self.client.post(login_url, login_data, format='json')
        
        assert login_response.status_code == status.HTTP_200_OK
        assert login_response.data['user']['role'] == Role.MANAGER


@pytest.mark.django_db
class TestSecurityIntegration:
    """Integration tests for security features."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = APIClient()
    
    def test_token_security_lifecycle(self):
        """Test the complete token security lifecycle."""
        # Create user and get tokens
        user = UserFactory(email='security@example.com')
        user.set_password('securepass123')
        user.save()
        
        # Login to get tokens
        login_data = {
            'email': 'security@example.com',
            'password': 'securepass123'
        }
        
        login_url = reverse('authentication:login')
        login_response = self.client.post(login_url, login_data, format='json')
        
        access_token = login_response.data['access']
        refresh_token = login_response.data['refresh']
        
        # Use access token to access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_url = reverse('authentication:profile')
        
        # Should be able to access with valid token
        response = self.client.get(profile_url)
        assert response.status_code == status.HTTP_200_OK
        
        # Logout (blacklist refresh token)
        logout_url = reverse('authentication:logout')
        logout_data = {'refresh': refresh_token}
        logout_response = self.client.post(logout_url, logout_data, format='json')
        
        assert logout_response.status_code == status.HTTP_205_RESET_CONTENT
        
        # Try to use blacklisted refresh token to get new access token
        refresh_url = reverse('authentication:token_refresh')
        refresh_data = {'refresh': refresh_token}
        refresh_response = self.client.post(refresh_url, refresh_data, format='json')
        
        # Should fail because token is blacklisted
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_concurrent_user_sessions(self):
        """Test multiple concurrent sessions for the same user."""
        user = UserFactory(email='concurrent@example.com')
        user.set_password('testpass123')
        user.save()
        
        # Create multiple clients for same user
        client1 = APIClient()
        client2 = APIClient()
        
        login_data = {
            'email': 'concurrent@example.com',
            'password': 'testpass123'
        }
        
        login_url = reverse('authentication:login')
        
        # Login from client 1
        response1 = client1.post(login_url, login_data, format='json')
        assert response1.status_code == status.HTTP_200_OK
        
        # Login from client 2
        response2 = client2.post(login_url, login_data, format='json')
        assert response2.status_code == status.HTTP_200_OK
        
        # Both should have different tokens
        assert response1.data['access'] != response2.data['access']
        assert response1.data['refresh'] != response2.data['refresh']
        
        # Both should be able to access protected endpoints
        client1.credentials(HTTP_AUTHORIZATION=f'Bearer {response1.data["access"]}')
        client2.credentials(HTTP_AUTHORIZATION=f'Bearer {response2.data["access"]}')
        
        profile_url = reverse('authentication:profile')
        
        profile1 = client1.get(profile_url)
        profile2 = client2.get(profile_url)
        
        assert profile1.status_code == status.HTTP_200_OK
        assert profile2.status_code == status.HTTP_200_OK
    
    def test_role_based_access_control(self):
        """Test role-based access control across the system."""
        # Create users with different roles
        admin = UserFactory(email='admin@test.com', role=Role.ADMIN)
        admin.set_password('adminpass123')
        admin.is_staff = True
        admin.save()
        
        manager = UserFactory(email='manager@test.com', role=Role.MANAGER)
        manager.set_password('managerpass123')
        manager.save()
        
        employee = UserFactory(email='employee@test.com', role=Role.EMPLOYEE)
        employee.set_password('employeepass123')
        employee.save()
        
        # Create profiles
        UserProfileFactory(user=admin)
        UserProfileFactory(user=manager)
        UserProfileFactory(user=employee)
        
        # Test that each user can access their own profile
        for user, password in [
            (admin, 'adminpass123'),
            (manager, 'managerpass123'),
            (employee, 'employeepass123')
        ]:
            client = APIClient()
            
            # Login
            login_data = {'email': user.email, 'password': password}
            login_response = client.post(reverse('authentication:login'), login_data, format='json')
            
            assert login_response.status_code == status.HTTP_200_OK
            assert login_response.data['user']['role'] == user.role
            
            # Access own profile
            client.credentials(HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}')
            profile_response = client.get(reverse('authentication:profile'))
            
            assert profile_response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestErrorHandlingIntegration:
    """Integration tests for error handling scenarios."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = APIClient()
    
    def test_registration_error_scenarios(self):
        """Test various registration error scenarios."""
        registration_url = reverse('authentication:register')
        
        # Test missing required fields
        incomplete_data = {
            'email': 'incomplete@example.com',
            'password': 'testpass123'
            # Missing password_confirm, role, first_name, last_name
        }
        
        response = self.client.post(registration_url, incomplete_data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Test invalid email format
        invalid_email_data = {
            'email': 'invalid-email-format',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
            'role': Role.EMPLOYEE,
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = self.client.post(registration_url, invalid_email_data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_authentication_error_scenarios(self):
        """Test various authentication error scenarios."""
        # Create a user
        user = UserFactory(email='test@example.com')
        user.set_password('correctpassword')
        user.save()
        
        login_url = reverse('authentication:login')
        
        # Test wrong password
        wrong_password_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(login_url, wrong_password_data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test non-existent user
        nonexistent_data = {
            'email': 'nonexistent@example.com',
            'password': 'anypassword'
        }
        
        response = self.client.post(login_url, nonexistent_data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test inactive user
        user.is_active = False
        user.save()
        
        inactive_data = {
            'email': 'test@example.com',
            'password': 'correctpassword'
        }
        
        response = self.client.post(login_url, inactive_data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_token_error_scenarios(self):
        """Test various token-related error scenarios."""
        # Test access with invalid token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        
        profile_url = reverse('authentication:profile')
        response = self.client.get(profile_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test refresh with invalid token
        refresh_url = reverse('authentication:token_refresh')
        invalid_refresh_data = {'refresh': 'invalid_refresh_token'}
        
        response = self.client.post(refresh_url, invalid_refresh_data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
