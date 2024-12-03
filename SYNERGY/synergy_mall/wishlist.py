# wishlist.py

from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied, ValidationError
from .models import Wishlist, WishlistItem, Product
from django.utils import timezone


class WishlistService:
    def __init__(self, user):
        self.user = user

    def create_wishlist(self, title, description=None, privacy='private', expiry_date=None):
        """
        Create a new wishlist for the user.
        Ensure the title is unique and prevent 'General List'.
        """
        # Prevent creating a wishlist titled 'General List'
        if title.strip().lower() == "general list":
            raise ValidationError("You cannot create a wishlist titled 'General List'. It is reserved.")

        # Check for unique title
        if Wishlist.objects.filter(user=self.user, title__iexact=title.strip()).exists():
            raise ValidationError(f"A wishlist with the title '{title}' already exists. Please choose a different name.")

        # Create the wishlist if validations pass
        wishlist = Wishlist.objects.create(
            user=self.user,
            title=title.strip(),  # Clean up extra spaces
            description=description,
            privacy=privacy,
            expiry_date=expiry_date,
        )
        return wishlist

    def delete_wishlist(self, wishlist_id):
        try:
            # Ensure the wishlist belongs to the user
            wishlist = Wishlist.objects.get(id=wishlist_id, user=self.user)

            # Prevent deletion of the "General List"
            if wishlist.title == "General List":
                raise ValidationError("The 'General List' wishlist cannot be deleted.")

            # Delete the wishlist
            wishlist.delete()
        except Wishlist.DoesNotExist:
            raise ValidationError("Wishlist not found.")

    def update_wishlist(self, wishlist_id, title=None, description=None, privacy=None, expiry_date=None):
        """
        Edit an existing wishlist.
        Restrict edits to title, privacy, and expiry_date for the 'General List'.
        """
        wishlist = self._get_user_wishlist(wishlist_id)

        if wishlist.title == "General List":
            # Only allow updating the description for 'General List'
            if description is not None:
                wishlist.description = description
            else:
                raise ValidationError("You can only update the description of the 'General List' wishlist.")
        else:
            # Allow full edits for other wishlists
            if title:
                wishlist.title = title
            if description is not None:
                wishlist.description = description
            if privacy:
                wishlist.privacy = privacy
            if expiry_date:
                wishlist.expiry_date = expiry_date

        wishlist.save()
        return wishlist

    def get_user_wishlists(self):
        """
        Get all wishlists for the logged-in user.
        """
        return Wishlist.objects.filter(user=self.user)

    def get_wishlist(self, wishlist_id):
        """
        Get a specific wishlist. Handles permission checks for privacy.
        """
        wishlist = get_object_or_404(Wishlist, id=wishlist_id)

        # If wishlist is private and doesn't belong to the user, deny access
        if wishlist.privacy == 'private' and wishlist.user != self.user:
            raise PermissionDenied("You do not have access to this wishlist.")
        return wishlist

    def _get_user_wishlist(self, wishlist_id):
        """
        Internal helper to ensure the wishlist belongs to the current user.
        """
        wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=self.user)
        return wishlist

    def add_item_to_wishlist(self, wishlist_id, product_id, quantity=1):
        """
        Add a product to a user's wishlist.
        """
        wishlist = self._get_user_wishlist(wishlist_id)
        product = get_object_or_404(Product, id=product_id)
        WishlistItem.objects.create(
            wishlist=wishlist,
            product=product,
            quantity=quantity
        )

