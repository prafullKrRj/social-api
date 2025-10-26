from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User
from posts.models import Post
from social.models import Follow
from django.utils import timezone
from datetime import timedelta


class FollowUserViewTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@test.com', password='pass123')
        self.user2 = User.objects.create_user(username='user2', email='user2@test.com', password='pass123')
        self.user3 = User.objects.create_user(username='user3', email='user3@test.com', password='pass123')
        self.client.force_authenticate(user=self.user1)

    def test_follow_user_success(self):
        url = reverse('follow-user', kwargs={'pk': self.user2.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Follow.objects.filter(follower=self.user1, following=self.user2).exists())

    def test_follow_user_already_following(self):
        Follow.objects.create(follower=self.user1, following=self.user2)
        url = reverse('follow-user', kwargs={'pk': self.user2.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('already following', response.data['message'])

    def test_follow_self(self):
        url = reverse('follow-user', kwargs={'pk': self.user1.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cannot follow yourself', response.data['error'])

    def test_follow_nonexistent_user(self):
        url = reverse('follow-user', kwargs={'pk': 9999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_follow_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse('follow-user', kwargs={'pk': self.user2.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UnfollowUserViewTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@test.com', password='pass123')
        self.user2 = User.objects.create_user(username='user2', email='user2@test.com', password='pass123')
        self.client.force_authenticate(user=self.user1)

    def test_unfollow_user_success(self):
        Follow.objects.create(follower=self.user1, following=self.user2)
        url = reverse('unfollow-user', kwargs={'pk': self.user2.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Follow.objects.filter(follower=self.user1, following=self.user2).exists())

    def test_unfollow_user_not_following(self):
        url = reverse('unfollow-user', kwargs={'pk': self.user2.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not following', response.data['error'])

    def test_unfollow_nonexistent_user(self):
        url = reverse('unfollow-user', kwargs={'pk': 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unfollow_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse('unfollow-user', kwargs={'pk': self.user2.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FollowersListViewTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@test.com', password='pass123')
        self.user2 = User.objects.create_user(username='user2', email='user2@test.com', password='pass123')
        self.user3 = User.objects.create_user(username='user3', email='user3@test.com', password='pass123')
        self.client.force_authenticate(user=self.user1)

    def test_list_followers(self):
        Follow.objects.create(follower=self.user2, following=self.user1)
        Follow.objects.create(follower=self.user3, following=self.user1)
        url = reverse('followers')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_list_followers_empty(self):
        url = reverse('followers')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_list_followers_pagination(self):
        for i in range(4, 19):
            user = User.objects.create_user(username=f'user{i}', email=f'user{i}@test.com', password='pass123')
            Follow.objects.create(follower=user, following=self.user1)
        url = reverse('followers')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('next'))
        self.assertTrue(len(response.data['results']) <= 10)

    def test_list_followers_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse('followers')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FeedViewTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@test.com', password='pass123')
        self.user2 = User.objects.create_user(username='user2', email='user2@test.com', password='pass123')
        self.user3 = User.objects.create_user(username='user3', email='user3@test.com', password='pass123')
        self.client.force_authenticate(user=self.user1)

    def test_feed_shows_following_posts(self):
        Follow.objects.create(follower=self.user1, following=self.user2)
        Post.objects.create(author=self.user2, content='Post from user2')
        Post.objects.create(author=self.user3, content='Post from user3')
        url = reverse('feed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['content'], 'Post from user2')

    def test_feed_empty_when_not_following(self):
        Post.objects.create(author=self.user2, content='Post from user2')
        url = reverse('feed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_feed_multiple_following_users(self):
        Follow.objects.create(follower=self.user1, following=self.user2)
        Follow.objects.create(follower=self.user1, following=self.user3)
        Post.objects.create(author=self.user2, content='Post from user2')
        Post.objects.create(author=self.user3, content='Post from user3')
        url = reverse('feed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_feed_ordered_by_created_at(self):
        Follow.objects.create(follower=self.user1, following=self.user2)
        now = timezone.now()
        post1 = Post.objects.create(author=self.user2, content='First post')
        post1.created_at = now - timedelta(seconds=10)
        post1.save()
        post2 = Post.objects.create(author=self.user2, content='Second post')
        post2.created_at = now
        post2.save()
        url = reverse('feed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['content'], 'Second post')

    def test_feed_pagination(self):
        Follow.objects.create(follower=self.user1, following=self.user2)
        for i in range(15):
            Post.objects.create(author=self.user2, content=f'Post {i}')
        url = reverse('feed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('next'))
        self.assertTrue(len(response.data['results']) <= 10)

    def test_feed_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse('feed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FollowModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@test.com', password='pass123')
        self.user2 = User.objects.create_user(username='user2', email='user2@test.com', password='pass123')

    def test_follow_creation(self):
        follow = Follow.objects.create(follower=self.user1, following=self.user2)
        self.assertIsNotNone(follow.created_at)
        self.assertEqual(follow.follower, self.user1)
        self.assertEqual(follow.following, self.user2)

    def test_unique_follow_constraint(self):
        Follow.objects.create(follower=self.user1, following=self.user2)
        with self.assertRaises(Exception):
            Follow.objects.create(follower=self.user1, following=self.user2)

    def test_follow_reverse_relation(self):
        Follow.objects.create(follower=self.user1, following=self.user2)
        self.assertEqual(self.user2.followers.count(), 1)
        self.assertEqual(self.user1.following.count(), 1)
