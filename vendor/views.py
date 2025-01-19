import random
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

import vendor
from .serializers import *
from .models import *
from rest_framework import generics, status


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
        status = self.request.query_params.get('status',None)

        if status:
            queryset =queryset.filter(is_approved=status)

        return queryset


# Generate and Send OTP via Email
def generate_and_send_otp(vendor):
    """Generate a new OTP and send it via email."""
    otp = str(random.randint(100000, 999999))
    vendor.otp = otp
    vendor.otp_expiry = timezone.now() + timedelta(minutes=5)
    vendor.save()

    try:
        send_mail(
            'Your Login OTP',
            f'Your OTP login code is {otp}.',
            'praveen.codeedex@gmail.com',  # Replace with your sender email
            [vendor.email],
            fail_silently=False
        )
    except Exception as e:
        return Response({'error': f'Failed to send OTP: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VendorLoginView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = VendorLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        vendor = Vendors.objects.filter(email=email).first()
        if not vendor:
            return Response({"error": "Vendor Not Found"}, status=status.HTTP_404_NOT_FOUND)

        if not vendor.is_approved:
            return Response({"error": "Your account has not been approved yet. Please contact support."},
                            status=status.HTTP_403_FORBIDDEN)

        generate_and_send_otp(vendor)
        return Response({"message": "OTP sent to email"}, status=status.HTTP_200_OK)
    

class VendorOTPVerifyView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = VendorOtpVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        vendor_admin = Vendors.objects.filter(email=email).first()
        if not vendor_admin:
            return Response({"error": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if OTP matches
        if vendor_admin.otp != otp:
            generate_and_send_otp(vendor_admin)  # Send a new OTP
            return Response({"error": "Invalid OTP. A new OTP has been sent to your email."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if OTP is expired
        if vendor_admin.otp_expiry and vendor_admin.otp_expiry < timezone.now():
            generate_and_send_otp(vendor_admin)
            return Response({"error": "OTP has expired. A new OTP has been sent to your email."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Clear OTP after successful verification
        vendor_admin.otp = None
        vendor_admin.otp_expiry = None
        vendor_admin.save()

        return Response({
            "message": "OTP verified successfully",
            "vendor_admin_id": vendor_admin.id
        }, status=status.HTTP_200_OK)

class VendorApprovalStatusView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        vendor_id = kwargs.get('id')
        try:
            vendor = Vendors.objects.get(id=vendor_id)
        except Vendors.DoesNotExist:
            return Response({'error': 'Vendor Not Found'}, status=status.HTTP_404_NOT_FOUND)

        # Serializer the vendor object and return the response
        serializer = VendorSerializer(vendor)
        return Response(serializer.data, status=status.HTTP_200_OK)

