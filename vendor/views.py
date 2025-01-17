from django.shortcuts import render
from pyexpat.errors import messages
from rest_framework.response import Response

from . serializers import *
from .models import *
from rest_framework import generics,status


# Create your views here.
class VendorListViews(generics.ListCreateAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Vendors.objects.all()
    serializer_class = VendorSerializer

class VendorDetailViews(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Vendors.objects.all()
    serializer_class = VendorSerializer

class VendorAdminListViews(generics.ListAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Vendors.objects.all()
    serializer_class = VendorSerializer

class VendorAdminDetailViews(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    authentication_classes = []
    serializer_class = VendorSerializer

    def get_queryset(self):
        return Vendors.objects.all()

    def get_object(self):
        vendor_id = self.kwargs.get("pk")
        try:
            return Vendors.objects.get(id=vendor_id)
        except Vendors.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Vendor not found.")

class VendorAdminAcceptReject(generics.UpdateAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Vendors.objects.all()
    serializer_class = VendorSerializer

    def update(self, request, *args, **kwargs):
        vendor = self.get_object()
        approval_status = request.data.get('is_approved', None)

        # Normalize input to boolean
        if approval_status in [True, 'true', 'True', 1, '1']:
            approval_status = True
        elif approval_status in [False, 'false', 'False', 0, '0']:
            approval_status = False
        else:
            return Response({'error': 'Invalid status. Must be a boolean (True/False).'}, status=status.HTTP_400_BAD_REQUEST)

        vendor.is_approved = approval_status
        vendor.save()

        return Response(
            {'status': 'Vendor registration approved.' if approval_status else 'Vendor registration rejected.'},
            status=status.HTTP_200_OK
        )

#for enable or disable vendors-Admin
class VendorEnbaleDisableView(generics.UpdateAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Vendors.objects.all()
    serializer_class = VendorSerializer

    def update(self, request, *args, **kwargs):
        vendor = self.get_object()
        enable_status = request.data.get('is_active')
        if isinstance(enable_status,str):
            enable_status = enable_status.lower() in ["true","1"]
        if enable_status not in [True,False]:
            return Response({'error':'Invalid status.Must be a Boolean(True/False).'},status=status.HTTP_400_BAD_REQUEST)

        vendor.is_active = enable_status
        vendor.save()
        message = 'Vendor status enabled.' if enable_status else 'vendor status disabled'
        return Response({'status':message},status=status.HTTP_200_OK)

class VendorFilterListView(generics.ListAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Vendors.objects.all()
    serializer_class = VendorSerializer
    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.queryser_params.get('status',None)

        if status:
            queryset =queryset.filter(is_approved=status)

        return queryset
