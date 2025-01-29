from django.urls import path
from purple.views.userdetails import *


urlpatterns=[
    path('admin-login/', AdminLoginView.as_view(), name='admin-login'),

    path('register/',RegisterView.as_view(),name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('request-otp/',RequestOTPView.as_view(),name='request-otp'),
    path('login/',LoginView.as_view(),name='login'),

    path('addresses/', AddressAPIView.as_view(), name='address-list'),  # List & Create
    path('addresses/<int:pk>/',AddressUpdateView.as_view(),name='address-detail'),

    path('users/update/', UserUpdateView.as_view(), name='user-update'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/', UserListView.as_view(), name='user-list'),

    path('category/',CategoryListView.as_view(),name='category-list'),
    path('category/<int:pk>/',CategoryDeatilView.as_view(),name='category-details'),

    path('carousel/',CarouselListView.as_view(),name='carousel-list'),
    path('carousel/<int:pk>/',CarouselDetailView.as_view(),name='carouesl-details'),




]