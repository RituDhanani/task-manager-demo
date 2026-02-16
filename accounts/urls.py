from django.urls import path
from .views import SignupAPIView, LoginAPIView, RefreshTokenAPIView, ChangePasswordAPIView

urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('token/refresh/', RefreshTokenAPIView.as_view(), name='token_refresh'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change_password'),
]