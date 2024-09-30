from django.db import models
from users.models import User
from django.conf import settings
from django.utils import timezone
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'vendor'})  # Restrict to vendor users
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', blank=True)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=50, blank=True, null=True)
    available = models.BooleanField(default=True)
    popularity_count = models.IntegerField(default=0)
    condition = models.CharField(max_length=50, choices=[('new', 'New'), ('used', 'Used'), ('refurbished', 'Refurbished')])
    image = models.ImageField(upload_to='media/products/')
    color = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    sale_start_date = models.DateTimeField(blank=True, null=True)
    sale_end_date = models.DateTimeField(blank=True, null=True)

    def is_on_sale(self):
        now = timezone.now()
        return self.sale_start_date and self.sale_end_date and self.sale_start_date <= now <= self.sale_end_date

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='media/product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"


# ## ORDER AND CART ##
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'regular'})  # Restrict to regular users
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered')])
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order by {self.user.username} for {self.product.name}"


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart ({self.user if self.user else 'Anonymous'})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ## WISHLIST MODELS ##

class Wishlist(models.Model):
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='private')
    shareable_link = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def is_expired(self):
        return self.expiry_date and timezone.now() > self.expiry_date


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('partial', 'Partially Filled'), ('filled', 'Filled')], default='Pending')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.product.name} in {self.wishlist.title}"


class CustomItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="custom_items")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Custom Item: {self.name} in {self.wishlist.title}"
