# Generated by Django 4.2 on 2023-06-10 14:15

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shop', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at')),
                ('delivery_type', models.CharField(choices=[('OR', 'ordinary'), ('EX', 'express')], default='OR', max_length=2, verbose_name='delivery type')),
                ('status', models.CharField(choices=[('CT', 'cart'), ('ED', 'editing'), ('AC', 'accepted'), ('RJ', 'rejected'), ('CO', 'completed')], default='ED', max_length=2, verbose_name='status')),
                ('city', models.CharField(blank=True, max_length=255, null=True, verbose_name='city')),
                ('address', models.TextField(blank=True, max_length=1024, null=True, verbose_name='address')),
                ('comment', models.TextField(blank=True, max_length=1024, null=True, verbose_name='comment')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this order should be treated as active. Unselect this instead of deleting orders.', verbose_name='active')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'order',
                'verbose_name_plural': 'orders',
            },
        ),
        migrations.CreateModel(
            name='OrderedProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='price')),
                ('count', models.SmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(0)], verbose_name='count')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.order', verbose_name='order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shop.product', verbose_name='product')),
            ],
            options={
                'verbose_name': 'ordered product',
                'verbose_name_plural': 'ordered products',
                'unique_together': {('product', 'order')},
            },
        ),
    ]
