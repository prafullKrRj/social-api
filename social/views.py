from django.core.serializers import serialize, get_serializer
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from posts.serializers import PostSerializer
from social.models import Follow
from social.serializer import FollowSerializer, FollowerListSerializer, FollowingListSerializer

from posts.models import Post  # Import your Post model


# Create your views here.

class FollowUserView(APIView):  # (POST) - follow a user
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_to_follow_id = kwargs.get('pk')

        # 1. Validate that the user to follow exists
        try:
            user_to_follow = User.objects.get(id=user_to_follow_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # 2. Validate that user is not trying to follow themselves
        if request.user.id == user_to_follow.id:
            return Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Create the relationship, or inform the user if it already exists
        # get_or_create returns a tuple: (object, created_boolean)
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )

        if not created:
            return Response({"message": "You are already following this user."}, status=status.HTTP_200_OK)

        # 4. Serialize the new follow relationship and return it
        serializer = FollowSerializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UnfollowUserView(APIView):  # (DELETE)
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user_to_unfollow_id = kwargs.get('pk')
        try:
            user_to_unfollow = User.objects.get(id=user_to_unfollow_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # The 'delete()' method returns a tuple: (number_of_objects_deleted, dict_with_deletions_per_model)
        deleted_count, _ = Follow.objects.filter(
            follower=request.user,
            following=user_to_unfollow
        ).delete()

        if deleted_count == 0:
            return Response({"error": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowersListView(ListAPIView):  # (GET) - who follows me
    permission_classes = [IsAuthenticated]
    serializer_class = FollowerListSerializer

    def get_queryset(self):
        # We want to find all 'Follow' objects where the 'following' user is the current user
        return self.request.user.followers.all()


class FollowingListView(ListAPIView):  # (GET) - who I follow
    permission_classes = [IsAuthenticated]
    serializer_class = FollowingListSerializer

    def get_queryset(self):
        # We want to find all 'Follow' objects where the 'follower' is the current user
        return self.request.user.following.all()


class FeedView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer  # You'll need to create this

    def get_queryset(self):
        following_users = self.request.user.following.values_list('following', flat=True)

        return Post.objects.filter(
            author_id__in=following_users
        ).select_related('author').order_by('-created_at')
