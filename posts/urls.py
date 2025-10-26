from django.urls import path

from posts.views import PostListCreateView, PostDetailView, UserPostsView

app_name = 'posts'

urlpatterns = [
    path('', PostListCreateView.as_view(), name='postsAll'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('user/<int:pk>/', UserPostsView.as_view(), name='user-posts')
]
