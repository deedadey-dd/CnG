from django.contrib.auth import get_user_model
from .models import Wishlist

User = get_user_model()


def create_general_wishlists():
    users = User.objects.all()
    for user in users:
        # Check if the user already has a "General List"
        if not Wishlist.objects.filter(user=user, title="General List").exists():
            Wishlist.objects.create(user=user, title="General List")
            print(f"General List created for user: {user.username}")
        else:
            print(f"User {user.username} already has a General List")
