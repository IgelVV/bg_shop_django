# Generated by Django 4.2 on 2023-05-14 13:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_category_is_active_category_sort_index_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='archived',
        ),
    ]
