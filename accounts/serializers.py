from rest_framework import serializers

from accounts.models import User, UserInfo
from posts.models import Post


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['password', 'password2', 'email', 'username', 'tc']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Passwords Don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True)


class UserLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        from rest_framework_simplejwt.tokens import RefreshToken
        try:
            RefreshToken(attrs['refresh'])
        except Exception as e:
            raise serializers.ValidationError("Invalid refresh token") from e
        return attrs


# this is the protected one only the user himself can see this information
class UserProfileSerializer(serializers.ModelSerializer):
    # changed to explicit safe fields to avoid exposing password/hash
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'createdAt', 'updatedAt', 'is_active', 'is_staff']
        read_only_fields = fields


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class UserInfoSerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()

    class Meta:
        model = UserInfo
        fields = '__all__'

    def get_posts_count(self, obj):
        return obj.user.posts.count()

    def get_posts(self, obj):
        return PostSerializer(obj.user.posts.all(), many=True).data


# this is the public information can be visible to anyone out there
class UserDetailSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'createdAt', 'info']

    def get_info(self, obj):
        if hasattr(obj, 'info'):
            return UserInfoSerializer(obj.info).data
        return None
