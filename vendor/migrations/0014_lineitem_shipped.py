# Generated by Django 5.0.7 on 2024-10-17 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0013_purchaseorderdetail_received_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineitem',
            name='shipped',
            field=models.IntegerField(default=1),
        ),
    ]