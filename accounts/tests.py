from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date

from accounts.models import User, UserInfo


class UserModelTestCase(TestCase):
    """Test cases for User and UserInfo models"""

    def setUp(self):
        """Set up test data that will be used across multiple tests"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'tc': True
        }

    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(**self.user_data)
        # self.assertEqual(user.objects, {
        #     'username': 'testuser',
        #     'email': 'test@example.com',
        #     'password': 'testpass123',
        #     'tc': True
        # })
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser"""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )

        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.tc)

    def test_user_info_created_automatically(self):
        """Test that UserInfo is automatically created when User is created"""
        user = User.objects.create_user(**self.user_data)

        self.assertTrue(hasattr(user, 'info'))
        self.assertIsInstance(user.info, UserInfo)

    def test_user_string_representation(self):
        """Test the __str__ method returns username"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser')

    def test_user_without_username_or_email_raises_error(self):
        """Test that creating user without username and email raises ValueError"""
        with self.assertRaises(ValueError):
            User.objects.create_user(username='', email='', password='test123')


class UserRegistrationTestCase(APITestCase):
    """Test cases for user registration endpoint"""

    def setUp(self):
        self.register_url = reverse('register')
        self.valid_user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password2': 'securepass123',
            'tc': True
        }

    def test_register_user_success(self):
        """Test successful user registration"""
        response = self.client.post(self.register_url, self.valid_user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('access', response.data['token'])
        self.assertIn('refresh', response.data['token'])

        # Verify user was created in database
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_user_password_mismatch(self):
        """Test registration fails when passwords don't match"""
        invalid_data = self.valid_user_data.copy()
        invalid_data['password2'] = 'differentpass'

        response = self.client.post(self.register_url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_register_user_duplicate_username(self):
        """Test registration fails with duplicate username"""
        User.objects.create_user(
            username='newuser',
            email='other@example.com',
            password='pass123'
        )

        response = self.client.post(self.register_url, self.valid_user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_duplicate_email(self):
        """Test registration fails with duplicate email"""
        User.objects.create_user(
            username='otheruser',
            email='newuser@example.com',
            password='pass123'
        )

        response = self.client.post(self.register_url, self.valid_user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_missing_required_fields(self):
        """Test registration fails when required fields are missing"""
        incomplete_data = {'username': 'incomplete'}

        response = self.client.post(self.register_url, incomplete_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTestCase(APITestCase):
    """Test cases for user login endpoint"""

    def setUp(self):
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='loginuser',
            email='login@example.com',
            password='loginpass123',
            tc=True
        )

    def test_login_with_valid_credentials(self):
        """Test successful login with correct credentials"""
        login_data = {
            'username': 'loginuser',
            'password': 'loginpass123'
        }

        response = self.client.post(self.login_url, login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('msg', response.data)
        self.assertEqual(response.data['msg'], 'Login Success')

    def test_login_with_email_instead_of_username(self):
        """Test login works with email in username field"""
        login_data = {
            'username': 'login@example.com',
            'password': 'loginpass123'
        }

        response = self.client.post(self.login_url, login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_with_wrong_password(self):
        """Test login fails with incorrect password"""
        login_data = {
            'username': 'loginuser',
            'password': 'wrongpassword'
        }

        response = self.client.post(self.login_url, login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('errors', response.data)

    def test_login_with_nonexistent_user(self):
        """Test login fails with non-existent username"""
        login_data = {
            'username': 'nonexistent',
            'password': 'somepassword'
        }

        response = self.client.post(self.login_url, login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_login_with_missing_fields(self):
        """Test login fails when required fields are missing"""
        response = self.client.post(self.login_url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLogoutTestCase(APITestCase):
    """Test cases for user logout endpoint"""

    def setUp(self):
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(
            username='logoutuser',
            email='logout@example.com',
            password='logoutpass123'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

    def test_logout_success(self):
        """Test successful logout with valid refresh token"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        logout_data = {'refresh': str(self.refresh)}
        response = self.client.post(self.logout_url, logout_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_without_authentication(self):
        """Test logout fails when user is not authenticated"""
        logout_data = {'refresh': str(self.refresh)}
        response = self.client.post(self.logout_url, logout_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_with_invalid_token(self):
        """Test logout fails with invalid refresh token"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        logout_data = {'refresh': 'invalid_token_string'}
        response = self.client.post(self.logout_url, logout_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileTestCase(APITestCase):
    """Test cases for user profile endpoint (authenticated user's own profile)"""

    def setUp(self):
        self.profile_url = reverse('profile')
        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='profilepass123'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

    def test_get_profile_authenticated(self):
        """Test authenticated user can retrieve their profile"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'profileuser')
        self.assertEqual(response.data['email'], 'profile@example.com')

    def test_get_profile_unauthenticated(self):
        """Test unauthenticated user cannot access profile"""
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_info(self):
        """Test updating user info (bio, website, etc.)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        update_data = {
            'bio': 'This is my bio',
            'website': 'https://example.com',
            'twitter_handle': '@profileuser'
        }

        response = self.client.patch(self.profile_url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'This is my bio')

        # Verify in database
        self.user.info.refresh_from_db()
        self.assertEqual(self.user.info.bio, 'This is my bio')

    def test_update_user_info_partial(self):
        """Test partial update of user info"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        update_data = {'phone_number': '+1234567890'}
        response = self.client.patch(self.profile_url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], '+1234567890')


class UserDetailTestCase(APITestCase):
    """Test cases for public user detail endpoint"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='publicuser',
            email='public@example.com',
            password='publicpass123'
        )
        # Update user info
        self.user.info.bio = 'Public bio'
        self.user.info.website = 'https://public.com'
        self.user.info.save()

        self.detail_url = reverse('detail', kwargs={'pk': self.user.pk})

    def test_get_user_detail_public(self):
        """Test anyone can view public user details"""
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'publicuser')
        self.assertIn('info', response.data)
        self.assertEqual(response.data['info']['bio'], 'Public bio')

    def test_get_user_detail_nonexistent(self):
        """Test retrieving non-existent user returns 404"""
        nonexistent_url = reverse('detail', kwargs={'pk': 99999})
        response = self.client.get(nonexistent_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_detail_includes_info(self):
        """Test that user detail includes user info object"""
        response = self.client.get(self.detail_url)

        self.assertIn('info', response.data)
        self.assertIsNotNone(response.data['info'])
        self.assertIn('bio', response.data['info'])
        self.assertIn('website', response.data['info'])


class UserInfoModelTestCase(TestCase):
    """Test cases for UserInfo model properties and methods"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='infouser',
            email='info@example.com',
            password='infopass123'
        )

    def test_user_info_posts_count_property(self):
        """Test posts_count property returns correct count"""
        # This assumes you have a Post model with user foreign key
        # Initially should be 0
        self.assertEqual(self.user.info.posts_count, 0)

    def test_user_info_fields_optional(self):
        """Test that UserInfo fields are optional and can be blank"""
        user_info = self.user.info

        self.assertEqual(user_info.bio, '')
        self.assertEqual(user_info.website, '')
        self.assertIsNone(user_info.birth_date)
        self.assertEqual(user_info.phone_number, '')

    def test_user_info_update(self):
        """Test updating UserInfo fields"""
        user_info = self.user.info
        user_info.bio = 'Updated bio'
        user_info.birth_date = date(1990, 1, 1)
        user_info.phone_number = '+1234567890'
        user_info.save()

        user_info.refresh_from_db()
        self.assertEqual(user_info.bio, 'Updated bio')
        self.assertEqual(user_info.birth_date, date(1990, 1, 1))


class TokenTestCase(TestCase):
    """Test cases for token generation helper function"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='tokenuser',
            email='token@example.com',
            password='tokenpass123'
        )

    def test_get_tokens_for_user(self):
        """Test that tokens are generated correctly for a user"""
        from accounts.views import get_tokens_for_user

        tokens = get_tokens_for_user(self.user)

        self.assertIn('refresh', tokens)
        self.assertIn('access', tokens)
        self.assertIsInstance(tokens['refresh'], str)
        self.assertIsInstance(tokens['access'], str)
        self.assertTrue(len(tokens['refresh']) > 0)
        self.assertTrue(len(tokens['access']) > 0)
