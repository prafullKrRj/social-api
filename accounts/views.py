from django.contrib.auth import authenticate

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from accounts.serializers import UserRegistrationSerializer, UserLoginSerializer, UserLogoutSerializer, \
    UserProfileSerializer, UserDetailSerializer, UserInfoSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterUserView(APIView):
    def post(self, request, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response(
            {'token': token},
            status=status.HTTP_201_CREATED
        )


class LoginUserView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user is None:
                return Response({'errors': {'non_field_errors': ['Email or Password is not Valid']}},
                                status=status.HTTP_404_NOT_FOUND)
            else:
                token = get_tokens_for_user(user)
                return Response(
                    {'token': token, 'msg': 'Login Success'}, status=status.HTTP_200_OK)
        return Response(data={
            "Message": "Bad credentials"
        }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserLogoutSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = serializer.validated_data["refresh"]
            token = RefreshToken(refresh_token)
            print(token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveAPIView, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        print(request.data)
        user = getattr(self.request, "user", None)
        user_info = user.info
        serializer = UserInfoSerializer(user_info, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserDetailSerializer
    lookup_field = 'pk'
    queryset = User.objects.get_queryset()
