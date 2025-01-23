from django.urls import path
from . views import *

urlpatterns=[
    path("vendors/",VendorListViews.as_view(),name="list vendors"),

    path('vendors/<int:pk>/',VendorDetailViews.as_view(),name="List-detail-vendors"),

    path('vendors-adminview/',VendorAdminListViews.as_view(),name="vendor-admin-list"),

    path('vendor-admin-deatilview/<int:pk>/',VendorAdminDetailViews.as_view(),name="vendor-detail-view"),

#accept reject vendors - (admin)
    path('vendor-accept-reject/<int:pk>/', VendorAdminAcceptReject.as_view(), name='vendor-admin-update'),

    path('vendor-enable-disable/<int:pk>/',VendorEnbaleDisableView.as_view(),name='vendor-Enable-disable'),
    
#filter-accept-reject
    path('vendor-fliter-list/',VendorFilterListView.as_view(),name='vendor-Fliter-list-view'),

#vendor Login
    path('vendor-login/',VendorLoginView.as_view(),name="vendor-login"),
#vendor Otp Verify
    path('vendor-otpverify/',VendorOTPVerifyView.as_view(),name='vendor-otp-verify'),

#vendor Approval Status
    path('vendor-approval-status/<int:id>/', VendorApprovalStatusView.as_view(), name='vendor-approval-status'),



]
