from django.urls import path
from . views import *

urlpatterns = [

    path('product/',ProductCreateListView.as_view(),name='product-list-create'),
    path('product/list',ProductCreateListView.as_view(),name='product-list'),
    path('product/<int:pk>/',ProductCreateDetailView.as_view(),name='product-details-list')




]