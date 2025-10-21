"""
/api/social/follow/<user_id>/
/api/social/unfollow/<user_id>/
/api/social/followers/
/api/social/following/
/api/social/feed/

"""
from django.urls import path

from social.views import FollowUserView, UnfollowUserView, FollowersListView, FeedView

urlpatterns = [
    path('follow/<int:pk>/', FollowUserView.as_view(), name='follow-user'),
    path('unfollow/<int:pk>/', UnfollowUserView.as_view(), name='unfollow-user'),
    path('followers/', FollowersListView.as_view(), name='followers'),
    path('feed/', FeedView.as_view(), name='feed')
]
