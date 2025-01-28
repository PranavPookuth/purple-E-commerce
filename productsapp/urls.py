from tkinter.font import names

from django.urls import path
from . views import *

urlpatterns = [

    path('product/',ProductCreateListView.as_view(),name='product-list-create'),
    path('product/list',ProductCreateListView.as_view(),name='product-list'),
    path('product/<int:pk>/',ProductCreateDetailView.as_view(),name='product-details-list'),

    path('singleproduct/<int:pk>/',SingleProductView.as_view(),name='single-product'),
    path('products/search/',ProductSearchView.as_view(),name='product-search'),
    path('offer/products',OfferProductsListView.as_view(),name='offer-products'),
    path('popular/products/',PopularPorductsListView.as_view(),name='popular-products'),

    path('vendors/<int:vendor_id>/products',VendorProductListView.as_view(),name='vendor-products-view'),
    path('vendors/<int:vendor_id>/categories/', VendorCategoryListView.as_view(), name='vendor-category-list'),


    path('wishlist/', WishlistView.as_view(), name='wishlist-view'),
    path('wishlist/add/',WishlistView.as_view(),name='wishlist-add'),
    path('wishlist/remove/',WishlistView.as_view(),name='wishlist-remove'),


    path('product/review/',ProductReviewCreateUpdateView.as_view(),name='product-review'),
    path('product/review/delete/<int:review_id>/', ProductReviewDeleteView.as_view(), name='delete-product-review'),



]