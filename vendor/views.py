from django.shortcuts import render
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
