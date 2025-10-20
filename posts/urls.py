from django.urls import path

from posts.views import PostListCreateView, PostDetailView, UserPostsView

urlpatterns = [
    path('', PostListCreateView.as_view(), name='postsAll'),
    path('<int:pk>/', PostDetailView.as_view()),
    path('user/<int:pk>/', UserPostsView.as_view())
]
