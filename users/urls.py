from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import (
    EmailVerificationViewSet,
    UserRegisterView,
    EmailConfirmView,
    UserLoginView,
    index
)

app_name = 'MainPage'

router = DefaultRouter()
router.register(r'email_verification', EmailVerificationViewSet, basename='email_verification')

urlpatterns = [
    path('', index, name='index'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('confirm_code/<uidb64>/<token>/', EmailConfirmView.as_view(), name='confirm_code'),
    path('api/', include(router.urls)),
]
