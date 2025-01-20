from django.urls import path
from . views import *

urlpatterns=[
    path('register/',RegisterView.as_view(),name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('request-otp/',RequestOTPView.as_view(),name='request-otp'),
    path('login/',LoginView.as_view(),name='login'),

    path('user/',UserListCreateView.as_view(),name='user-list'),
    path('user/<int:pk>/',UserDetailView.as_view(),name='user-details'),

    path('userprofile/',UserprofileListCreateView.as_view(),name='user-profile'),
    path('userprofile/<str:user__username>/',UserProfileDetailView.as_view(),name='user-detail'),

    path('category/',CategoryCreateView.as_view(),name='category'),
    path('category/<int:pk>/',CategoryDetailView.as_view(),name='category-details'),

    path('carousel/', CarouselListCreateView.as_view(), name='carousel-list-create'),
    path('carousel/<int:pk>/', CarouselDetailView.as_view(), name='carousel-detail'),

    path('bannerimage/', BannerImageListCreateView.as_view(), name='banner-image'),
    path('bannerimage/<int:pk>/', BannerDetailsView.as_view(), name='banner-details'),


    path('products/',ProductListCreateView.as_view(),name='product'),
    path('products/<int:pk>/',ProductDetailView.as_view(),name='product-details'),


    path('products/<int:product_id>/images/', ProductImageListView.as_view(), name='product-image-list'),
    path('products/images/<int:pk>/', ProductImageDetailView.as_view(), name='product-image-detail'),
    path('product-images/<int:pk>/', ProductImageDetailView.as_view(), name='product-image-detail'),

    path('singleproducts/<int:pk>/', SingleProductDetailView.as_view(), name='product-detail'),
    path('products/search/', ProductSearchView.as_view(), name='product-search'),

    path('add_to_cart/<int:user_id>/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('update_cart_item/<int:user_id>/<int:product_id>/', UpdateCartItemQuantityView.as_view(), name='update_cart_item'),
    path('user_cart_items/<int:user_id>/', UserCartView.as_view(), name='user_cart_items'),
    path('remove_from_cart/<int:user_id>/<int:product_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),

    path('checkout/cod/<int:user_id>/', CheckoutCODView.as_view(), name='checkout_cod'),

    path('orders/<int:user_id>/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:user_id>/<str:order_ids>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/', AllOrdersListView.as_view(), name='all-orders-list'),
    path('order/<int:pk>/', Allorderdetailview.as_view(), name='order-detail'),


]