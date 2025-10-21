from django.db.migrations import serializer
from rest_framework import serializers

from posts.models import Post


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'author', 'content', 'created_at')

    def get_author(self, obj):
        user = obj.author
        return {'id': user.id, 'username': getattr(user, 'username', None)}


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('content',)  # author will be set in the view

    def create(self, validated_data):
        print(validated_data)
        # actual author is attached in view.perform_create
        return super().create(validated_data)


class UserPostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'content', 'created_at']
