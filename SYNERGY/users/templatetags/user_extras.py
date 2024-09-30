# users/templatetags/user_extras.py
from django import template
from users.models import Vendor

register = template.Library()


@register.filter
def is_vendor(user):
    return user.is_authenticated and hasattr(user, 'vendor')
