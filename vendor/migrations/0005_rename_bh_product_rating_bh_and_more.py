# Generated by Django 5.0.7 on 2024-08-06 09:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0004_rename_vintage_product_additional_notes_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='bh',
            new_name='rating_bh',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='jg',
            new_name='rating_jg',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='js',
            new_name='rating_js',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='vm',
            new_name='rating_vm',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='wa',
            new_name='rating_wa',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='ws',
            new_name='rating_ws',
        ),
    ]
