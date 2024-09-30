from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.utils import timezone


# UserManager for custom user model
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


# Custom user model
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('vendor', 'Vendor'),
        ('regular', 'RegularUser'),
        ('marketer', 'Marketer'),
        ('manager', 'Manager'),
    )
    username = models.CharField(max_length=50, blank=False, null=False, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    other_names = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    id_document_number = models.CharField(max_length=100, blank=True, null=True)
    id_image = models.ImageField(upload_to='identification_images/', blank=True, null=True)
    default_shipping_address = models.TextField(max_length=400, blank=True, null=True)
    cash = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # Wallet/cash balance

    # New field for defining user roles
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # Resolve the clash by adding related_name
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',  # Adding related_name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',  # Adding related_name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


# Vendor-specific information, separate model linked to User
class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    phone_number2 = models.CharField(max_length=15, unique=True)
    company_name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    verification_status = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name
