# wishlist.py

from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from .models import Wishlist, WishlistItem, Product
from django.utils import timezone


class WishlistService:
    def __init__(self, user):
        self.user = user

    def create_wishlist(self, title, description=None, privacy='private', expiry_date=None):
        """
        Create a new wishlist for the user.
        """
        wishlist = Wishlist.objects.create(
            user=self.user,
            title=title,
            description=description,
            privacy=privacy,
            expiry_date=expiry_date,
        )
        return wishlist

    def delete_wishlist(self, wishlist_id):
        """
        Delete a wishlist owned by the user.
        """
        wishlist = self._get_user_wishlist(wishlist_id)
        wishlist.delete()

    def update_wishlist(self, wishlist_id, title, description=None, privacy='private', expiry_date=None):
        """
        Edit an existing wishlist.
        """
        wishlist = self._get_user_wishlist(wishlist_id)
        wishlist.title = title
        wishlist.description = description
        wishlist.privacy = privacy
        wishlist.expiry_date = expiry_date
        wishlist.save()

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

