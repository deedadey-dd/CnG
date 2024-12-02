from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from synergy_mall.models import Wishlist

User = get_user_model()


@receiver(post_save, sender=User)
def create_general_wishlist(sender, instance, created, **kwargs):
    """
    Signal to create a 'General List' wishlist for newly registered users.
    """
    if created:  # Only for newly created users
        Wishlist.objects.get_or_create(
            user=instance,
            title="General List"  # Default wishlist name
        )
