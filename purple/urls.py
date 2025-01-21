from django.urls import path
from purple.views.userdetails import *


urlpatterns=[
    path('admin-login/', AdminLoginView.as_view(), name='admin-login'),

    path('register/',RegisterView.as_view(),name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('request-otp/',RequestOTPView.as_view(),name='request-otp'),
    path('login/',LoginView.as_view(),name='login'),

    path('user/',UserListCreateView.as_view(),name='user-list'),
    path('user/<int:pk>/',UserDetailView.as_view(),name='user-details'),


]