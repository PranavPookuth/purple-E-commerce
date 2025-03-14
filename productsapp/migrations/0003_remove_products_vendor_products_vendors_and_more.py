# Generated by Django 5.1.1 on 2025-01-25 05:54

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productsapp', '0002_remove_products_vendors_products_vendor_and_more'),
        ('vendor', '0002_delete_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='products',
            name='vendor',
        ),
        migrations.AddField(
            model_name='products',
            name='vendors',
            field=models.ForeignKey(default=django.utils.timezone.now, on_delete=django.db.models.deletion.CASCADE, related_name='vendors', to='vendor.vendors'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='products',
            name='Popular_products',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='products',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='products',
            name='discount',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Discount Percentage', max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='products',
            name='isofferproduct',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='products',
            name='newarrival',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='products',
            name='product_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='products',
            name='trending_one',
            field=models.BooleanField(),
        ),
    ]
