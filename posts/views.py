from rest_framework.generics import RetrieveAPIView, ListCreateAPIView, ListAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponseForbidden, HttpResponse

from posts.models import Post
from posts.serializers import PostCreateSerializer, PostSerializer, UserPostsSerializer


class PostListCreateView(ListCreateAPIView):
    queryset = Post.objects.all()

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    # I have used this to get the posts which are not of the particular user as he/she does not want to see their posts in their feed it's going to be displayed in their profile
    def get_queryset(self):
        qs = super().get_queryset()
        user = getattr(self.request, "user", None)
        print(user)
        if self.request.method == "GET" and user and user.is_authenticated:
            return qs.exclude(author=user)
        return qs

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostCreateSerializer  # post serializer class and has authentication in here
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)  # in perform create setting the author


class PostDetailView(RetrieveAPIView, DestroyAPIView, UpdateAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method in ['DELETE', 'PUT', 'PATCH']:
            return [IsAuthenticated()]
        else:
            return [AllowAny()]

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return HttpResponseForbidden()
        post.delete()
        return HttpResponse(status=204)

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return HttpResponseForbidden()
        return super().update(request, *args, **kwargs)


class UserPostsView(ListAPIView):
    serializer_class = UserPostsSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        return Post.objects.filter(
            author_id=user_id
        ).select_related('author').order_by('-created_at')
