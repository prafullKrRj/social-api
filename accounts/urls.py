from django.urls import path

from accounts.views import RegisterUserView, LoginUserView, LogoutView, UserProfileView, UserDetailView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='detail'),
]
