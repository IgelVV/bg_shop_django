# Generated by Django 4.2 on 2023-07-12 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_config', '0002_auto_20230610_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dynamicconfig',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
