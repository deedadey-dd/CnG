# Generated by Django 5.1.1 on 2024-09-11 00:56

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=50, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(max_length=50)),
                ('surname', models.CharField(max_length=50)),
                ('other_names', models.CharField(blank=True, max_length=100, null=True)),
                ('phone_number', models.CharField(max_length=15, unique=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pictures/')),
                ('id_document_number', models.CharField(blank=True, max_length=100, null=True)),
                ('id_image', models.ImageField(blank=True, null=True, upload_to='identification_images/')),
                ('default_shipping_address', models.TextField(blank=True, max_length=400, null=True)),
                ('cash', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('role', models.CharField(choices=[('vendor', 'Vendor'), ('regular', 'RegularUser'), ('marketer', 'Marketer'), ('manager', 'Manager')], max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='custom_user_groups', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='custom_user_permissions', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number2', models.CharField(max_length=15, unique=True)),
                ('company_name', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('verification_status', models.BooleanField(default=False)),
                ('last_seen', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_profile', to='users.user')),
            ],
        ),
    ]
