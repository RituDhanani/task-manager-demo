from django.urls import path
from .views import (SignupAPIView, LoginAPIView, RefreshTokenAPIView,
                     ChangePasswordAPIView, ResetPasswordOTPRequestAPIView,
                     ResetPasswordOTPConfirmAPIView, UserProfileView)
urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('token/refresh/', RefreshTokenAPIView.as_view(), name='token_refresh'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change_password'),
    path('reset-password/', ResetPasswordOTPRequestAPIView.as_view(), name='reset_password_otp'),
    path('reset-password-confirm/', ResetPasswordOTPConfirmAPIView.as_view(), name='reset_password_otp_confirm'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),

]
