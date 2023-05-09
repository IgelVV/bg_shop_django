# Generated by Django 4.2 on 2023-05-09 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_alter_payment_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymenttype',
            name='name',
            field=models.CharField(choices=[('ON', 'online'), ('RN', 'random')], max_length=2, unique=True, verbose_name='name'),
        ),
    ]
