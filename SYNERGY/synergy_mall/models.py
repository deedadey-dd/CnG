from django.db import models
from users.models import User
from django.conf import settings
from django.utils import timezone
import uuid
from decimal import Decimal
from django.db import models


# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


# Product Model
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'vendor'})
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', blank=True)
    available = models.BooleanField(default=True)
    popularity_count = models.IntegerField(default=0)
    condition = models.CharField(max_length=50, choices=[('new', 'New'), ('used', 'Used'), ('refurbished', 'Refurbished')])
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    sale_start_date = models.DateTimeField(blank=True, null=True)
    sale_end_date = models.DateTimeField(blank=True, null=True)

    def is_on_sale(self):
        now = timezone.now()
        return self.sale_start_date and self.sale_end_date and self.sale_start_date <= now <= self.sale_end_date

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    color = models.CharField(max_length=50, blank=True, null=True)  # Optional: Some products may not have color variants
    size = models.CharField(max_length=20, blank=True, null=True)  # Optional: Some products may not have size variants
    sku = models.CharField(max_length=50, blank=True, null=True, unique=True)
    stock = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Variant-specific price
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Variant-specific sale price
    image = models.ImageField(upload_to='media/product_variants/', blank=True, null=True)

    def get_effective_price(self):
        """
        Calculate the effective price for the variant.
        If the product is on sale, apply the sale price of the variant or product.
        Otherwise, use the regular price.
        """
        if self.product.is_on_sale():
            return self.sale_price if self.sale_price else self.product.get_sale_price()
        return self.price if self.price else self.product.price

    def __str__(self):
        variant_str = f"{self.product.name}"
        if self.color:
            variant_str += f" - Color: {self.color}"
        if self.size:
            variant_str += f" - Size: {self.size}"
        return variant_str

    class Meta:
        unique_together = ('product', 'color', 'size')  # Ensure uniqueness for each color-size combination


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='media/product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"


# Tag Model for Product Tags
class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


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


# ## WISHLIST MODELS ##
class WishlistQuerySet(models.QuerySet):
    def not_expired(self):
        """Return wishlists that are either non-expired or have no expiry date."""
        return self.filter(
            models.Q(expiry_date__gt=timezone.now()) | models.Q(expiry_date__isnull=True)
        )

    def public(self):
        """Return only public wishlists."""
        return self.filter(privacy='public')


class WishlistManager(models.Manager):
    def get_queryset(self):
        return WishlistQuerySet(self.model, using=self._db)  # Use the custom QuerySet

    def not_expired(self):
        return self.get_queryset().not_expired()

    def public(self):
        return self.get_queryset().public()


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

    objects = WishlistManager()

    def __str__(self):
        return self.title

    def is_expired(self):
        return self.expiry_date and timezone.now() > self.expiry_date

    def total_cost(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

    def days_left(self):
        """Return the number of days left until expiry or None if no expiry date."""
        if self.expiry_date:
            remaining_time = self.expiry_date - timezone.now()
            if remaining_time.days > 0:
                return remaining_time.days
            else:
                return 0  # Return 0 if the expiry date has passed
        return None  # Return None if there is no expiry date

    def ordered_items(self):
        """Return the wishlist items ordered by the user's preference (ordering field)."""
        return self.items.all().order_by('ordering')

    def total_contributions(self):
        """Return the total amount of contributions for this wishlist."""
        # Sum contributions from both specific items and general contributions
        total_contributed = Decimal(0)
        # Add contributions for each wishlist item
        for item in self.items.all():
            total_contributed += item.amount_paid
        # Add general contributions (those without a specific item)
        general_contributions = self.contribution_set.filter(wishlist_item__isnull=True)
        for contribution in general_contributions:
            total_contributed += contribution.amount
        return total_contributed

    def remaining_cost(self):
        """Return the remaining amount to fully fund the wishlist."""
        return self.total_cost() - self.total_contributions()


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('partial', 'Partially Filled'), ('filled', 'Filled')], default='Pending')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ordering = models.PositiveIntegerField(default=0)  # Field to order items
    giver_contact = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} in {self.wishlist.title}"

    def total_price(self):
        return self.product.price * self.quantity

    def amount_remaining(self):
        """Return the remaining amount needed for this item."""
        total_price = self.product.price * self.quantity
        return max(total_price - self.amount_paid, 0)

    def is_fully_paid(self):
        """Return True if the item has been fully contributed for."""
        return self.amount_remaining() == 0


class CustomItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="custom_items")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Custom Item: {self.name} in {self.wishlist.title}"


# ###### CONTRIBUTIONS #################

class Contribution(models.Model):
    wishlist_item = models.ForeignKey(WishlistItem, on_delete=models.CASCADE, null=True, blank=True)  # Specific item
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)  # General wishlist contribution
    contributor_name = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255)  # Can hold either phone or email
    message = models.CharField(max_length=200, blank=True, null=True)  # Short message
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)  # Timestamp when the contribution is made

    def __str__(self):
        return f"Contribution of ${self.amount} by {self.contributor_name} to {self.wishlist.title}"


class Gift(models.Model):
    giver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gifts_sent',
        blank=True,  # Allow this field to be optional
        null=True    # Allow null values
    )
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gifts_received')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount_given = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
    giver_contact = models.CharField(max_length=255, blank=True, null=True)  # Contact is optional for authenticated users
    message_to_receiver = models.TextField(blank=True, null=True)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gift of {self.product.name} from {self.giver or 'Unauthenticated User'} to {self.receiver}"

