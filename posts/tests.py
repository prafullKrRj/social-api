from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User
from posts.models import Post


class PostModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_post_creation(self):
        post = Post.objects.create(
            author=self.user,
            content='Test post content'
        )
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.content, 'Test post content')
        self.assertTrue(post.created_at)

    def test_post_related_name(self):
        post = Post.objects.create(
            author=self.user,
            content='Test post'
        )
        self.assertIn(post, self.user.posts.all())


class PostListCreateViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )

    def test_get_posts_unauthenticated(self):
        Post.objects.create(author=self.user1, content='Post 1')
        response = self.client.get('/api/posts/')
        # print(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post_authenticated(self):
        self.client.force_authenticate(user=self.user1)
        data = {'content': 'New post content'}
        response = self.client.post('/api/posts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)

    def test_create_post_unauthenticated(self):
        data = {'content': 'New post content'}
        response = self.client.post('/api/posts/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PostDetailViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user1,
            content='Test post content'
        )

    def test_get_post_detail(self):
        response = self.client.get(f'/api/posts/{self.post.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_post_by_author(self):
        self.client.force_authenticate(user=self.user1)
        data = {'content': 'Updated content'}
        response = self.client.put(f'/api/posts/{self.post.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_post_by_non_author(self):
        self.client.force_authenticate(user=self.user2)
        data = {'content': 'Updated content'}
        response = self.client.put(f'/api/posts/{self.post.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_by_author(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f'/api/posts/{self.post.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class UserPostsViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        Post.objects.create(author=self.user1, content='Post 1')
        Post.objects.create(author=self.user1, content='Post 2')

    def test_get_user_posts(self):
        response = self.client.get(f'/api/posts/user/{self.user1.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
