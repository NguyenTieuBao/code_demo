from django.urls import path
from .controller import RegisterAPIView, LoginAPIView, LogoutAPIView, PasswordResetRequestAPIView, PasswordResetConfirmAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('reset-password/', PasswordResetRequestAPIView.as_view(), name='password-reset-request'),
    path('reset-password/<uuid:token>/', PasswordResetConfirmAPIView.as_view(), name='password-reset-confirm'),
]
