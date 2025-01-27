from django.urls import path
from . views import *

urlpatterns = [

    path('products/user/',ProductCreateView.as_view(),name='product-list'),

    path('product/',ProductCreateListView.as_view(),name='product-list-create'),
    path('product/list',ProductCreateListView.as_view(),name='product-list'),
    path('product/<int:pk>/',ProductCreateDetailView.as_view(),name='product-details-list'),

    path('singleproduct/<int:pk>/',SingleProductView.as_view(),name='single-product'),
    path('products/search/',ProductSearchView.as_view(),name='product-search'),

    path('vendors/<int:vendor_id>/products',VendorProductListView.as_view(),name='vendor-products-view'),
    path('vendors/<int:vendor_id>/categories/', VendorCategoryListView.as_view(), name='vendor-category-list'),



]