# Generated by Django 5.0.7 on 2024-10-17 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0015_lineitem_shipped_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorderdetail',
            name='expected_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
