from django.urls import path
from . views import *

urlpatterns=[
    path("vendors/",VendorListViews.as_view(),name="list vendors"),
]
