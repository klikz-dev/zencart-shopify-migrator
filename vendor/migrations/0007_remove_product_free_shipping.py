# Generated by Django 5.0.7 on 2024-07-30 14:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0006_alter_product_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='free_shipping',
        ),
    ]
