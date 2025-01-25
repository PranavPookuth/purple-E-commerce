from django.urls import path
from . views import *

urlpatterns = [

    path('products/',ProductListView.as_view(),name='product-list'),
    path('products/<int:pk>/',ProductDetailsView.as_view(),name='product-details'),



]