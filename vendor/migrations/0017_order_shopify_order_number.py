# Generated by Django 5.0.7 on 2024-10-25 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0016_purchaseorderdetail_expected_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shopify_order_number',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
    ]
