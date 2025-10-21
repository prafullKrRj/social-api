from rest_framework import serializers

from accounts.models import User
from social.models import Follow


class UserBasicSerializer(serializers.ModelSerializer):
    """A simple serializer to show basic user info."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class FollowSerializer(serializers.ModelSerializer):
    # Use the nested serializer and mark as read-only
    follower = UserBasicSerializer(read_only=True)
    following = UserBasicSerializer(read_only=True)

    class Meta:
        model = Follow
        # Add all fields you want to see in the response
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['id', 'created_at']


class FollowerListSerializer(serializers.ModelSerializer):
    """Serializer for listing followers."""
    follower = UserBasicSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['follower', 'created_at']


class FollowingListSerializer(serializers.ModelSerializer):
    """Serializer for listing who a user is following."""
    following = UserBasicSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['following', 'created_at']
