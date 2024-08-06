# Generated by Django 5.0.7 on 2024-08-06 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0006_remove_customer_address_address_customer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='billing_address1',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='billing_address2',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='billing_city',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='billing_company',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='billing_country',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='billing_name',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='billing_state',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='billing_zip',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_address_id',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
