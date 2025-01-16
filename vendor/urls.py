from django.urls import path
from . views import *

urlpatterns=[
    path("vendors/",VendorListViews.as_view(),name="list vendors"),
    path('vendors/<int:pk>/',VendorDetailViews.as_view(),name="List-detail-vendors"),
]
