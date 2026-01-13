"""
Comprehensive test suite for Accounts app.
Tests user registration, authentication, profile management, and password changes.
"""

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import User
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer
)


class UserModelTests(TestCase):
    """Tests for User model creation, validation, and methods."""
    
    def setUp(self):
        """Create test users."""
        self.user_data_b2c = {
            'email': 'customer@example.com',
            'password': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'B2C'
        }
        self.user_data_b2b = {
            'email': 'company@example.com',
            'password': 'testpass123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'B2B',
            'company_name': 'Test Company',
            'tax_id': 'TAX123'
        }
    
    def test_create_b2c_user(self):
        """Test creating a B2C user."""
        user = User.objects.create_user(**self.user_data_b2c)
        self.assertEqual(user.email, 'customer@example.com')
        self.assertEqual(user.role, 'B2C')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_create_b2b_user(self):
        """Test creating a B2B user with company details."""
        user = User.objects.create_user(**self.user_data_b2b)
        self.assertEqual(user.email, 'company@example.com')
        self.assertEqual(user.role, 'B2B')
        self.assertEqual(user.company_name, 'Test Company')
        self.assertEqual(user.tax_id, 'TAX123')
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_user_email_uniqueness(self):
        """Test that email must be unique."""
        User.objects.create_user(**self.user_data_b2c)
        with self.assertRaises(Exception):
            User.objects.create_user(**self.user_data_b2c)
    
    def test_user_string_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(**self.user_data_b2c)
        self.assertEqual(str(user), 'customer@example.com')
    
    def test_get_full_name(self):
        """Test get_full_name method."""
        user = User.objects.create_user(**self.user_data_b2c)
        self.assertEqual(user.get_full_name(), 'John Doe')
    
    def test_get_short_name(self):
        """Test get_short_name method."""
        user = User.objects.create_user(**self.user_data_b2c)
        self.assertEqual(user.get_short_name(), 'John')


class UserRegistrationTests(APITestCase):
    """Tests for user registration endpoint."""
    
    def setUp(self):
        """Initialize test client."""
        self.client = APIClient()
        self.register_url = reverse('user-register')
    
    def test_register_b2c_user(self):
        """Test successful B2C user registration."""
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'B2C'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().email, 'newuser@example.com')
    
    def test_register_b2b_user(self):
        """Test successful B2B user registration."""
        data = {
            'email': 'company@example.com',
            'password': 'companypass123',
            'password_confirm': 'companypass123',
            'first_name': 'Company',
            'last_name': 'Admin',
            'role': 'B2B',
            'company_name': 'Acme Corp',
            'tax_id': 'TAX456'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.first()
        self.assertEqual(user.company_name, 'Acme Corp')
    
    def test_register_password_mismatch(self):
        """Test registration fails if passwords don't match."""
        data = {
            'email': 'test@example.com',
            'password': 'pass123',
            'password_confirm': 'different123',
            'role': 'B2C'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
    
    def test_register_duplicate_email(self):
        """Test registration fails with duplicate email."""
        User.objects.create_user(
            email='existing@example.com',
            password='existpass123'
        )
        data = {
            'email': 'existing@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'role': 'B2C'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_b2b_without_company_name(self):
        """Test B2B registration requires company name."""
        data = {
            'email': 'b2b@example.com',
            'password': 'pass123',
            'password_confirm': 'pass123',
            'role': 'B2B'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_weak_password(self):
        """Test registration rejects passwords shorter than 8 characters."""
        data = {
            'email': 'test@example.com',
            'password': 'short',
            'password_confirm': 'short',
            'role': 'B2C'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTests(APITestCase):
    """Tests for user login endpoint."""
    
    def setUp(self):
        """Create test user."""
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        self.login_url = reverse('user-login')
    
    def test_login_success(self):
        """Test successful login."""
        data = {
            'email': 'testuser@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'testuser@example.com')
    
    def test_login_invalid_password(self):
        """Test login with wrong password."""
        data = {
            'email': 'testuser@example.com',
            'password': 'wrongpass123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent email."""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'anypass123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_missing_email(self):
        """Test login without email field."""
        data = {
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileTests(APITestCase):
    """Tests for user profile endpoints."""
    
    def setUp(self):
        """Create authenticated test user."""
        self.user = User.objects.create_user(
            email='profile@example.com',
            password='testpass123',
            first_name='Profile',
            last_name='User'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.profile_url = reverse('user-profile')
    
    def test_get_profile(self):
        """Test retrieving user profile."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'profile@example.com')
    
    def test_update_profile(self):
        """Test updating user profile."""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
    
    def test_update_profile_unauthenticated(self):
        """Test profile update requires authentication."""
        client = APIClient()
        data = {'first_name': 'Hacker'}
        response = client.patch(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChangePasswordTests(APITestCase):
    """Tests for password change endpoint."""
    
    def setUp(self):
        """Create authenticated test user."""
        self.user = User.objects.create_user(
            email='password@example.com',
            password='oldpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.change_password_url = reverse('user-change-password')
    
    def test_change_password_success(self):
        """Test successful password change."""
        data = {
            'old_password': 'oldpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        response = self.client.post(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))
    
    def test_change_password_wrong_old_password(self):
        """Test password change with wrong old password."""
        data = {
            'old_password': 'wrongold123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        response = self.client.post(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_change_password_mismatch(self):
        """Test password change fails if new passwords don't match."""
        data = {
            'old_password': 'oldpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'different123'
        }
        response = self.client.post(self.change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLogoutTests(APITestCase):
    """Tests for user logout endpoint."""
    
    def setUp(self):
        """Create authenticated test user."""
        self.user = User.objects.create_user(
            email='logout@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.logout_url = reverse('user-logout')
    
    def test_logout_success(self):
        """Test successful logout."""
        response = self.client.post(self.logout_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_logout_unauthenticated(self):
        """Test logout requires authentication."""
        client = APIClient()
        response = client.post(self.logout_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
