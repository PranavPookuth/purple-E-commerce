from django.contrib import admin
from django.contrib import admin
from .models import Vendors
# Register your models here.
@admin.register(Vendors)
class VendorsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'contact_number', 'is_active', 'is_approved', 'created_at')
    search_fields = ('name', 'email', 'contact_number')
    list_filter = ('is_active', 'is_approved', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('otp', 'otp_expiry', 'created_at')  # Prevent these fields from being edited directly
