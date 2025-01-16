from django.urls import path
from . views import *

urlpatterns=[
    path("vendors/",VendorListViews.as_view(),name="list vendors"),
    path('vendors/<int:pk>/',VendorDetailViews.as_view(),name="List-detail-vendors"),
    path('vendors-adminview/',VendorAdminListViews.as_view(),name="vendor-admin-list"),
    path('vendor-admin-deatilview/<int:pk>/',VendorAdminDetailViews.as_view(),name="vendor-detail-view"),

#accept reject vendors - (admin)
    path('vendor-accept-reject/<int:pk>/', VendorAdminAcceptReject.as_view(), name='vendor-admin-update'),


]
