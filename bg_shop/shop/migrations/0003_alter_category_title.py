# Generated by Django 4.2 on 2023-05-14 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_remove_product_date_product_release_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='title',
            field=models.CharField(max_length=255, unique=True, verbose_name='title'),
        ),
    ]
