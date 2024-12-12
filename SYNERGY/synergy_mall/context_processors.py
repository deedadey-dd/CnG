from .models import Cart


# def cart_items_count(request):
#     if request.user.is_authenticated:
#         cart = Cart.objects.filter(user=request.user).first()
#     else:
#         session_key = request.session.session_key
#         if not session_key:
#             request.session.create()
#             session_key = request.session.session_key
#         cart = Cart.objects.filter(session_key=session_key).first()
#
#     count = cart.items.count() if cart else 0
#     return {'cart_items_count': count}
#
#
# def cart_context(request):
#     """Provide the cart object for authenticated and guest users."""
#     cart = None
#     if request.user.is_authenticated:
#         cart = Cart.objects.filter(user=request.user).first()
#     else:
#         session_key = request.session.session_key
#         if not session_key:
#             request.session.create()
#             session_key = request.session.session_key
#         cart = Cart.objects.filter(session_key=session_key).first()
#
#     return {
#         "cart": cart
#     }

from .models import Cart


def get_cart(request):
    """Retrieve the active cart for authenticated or guest users."""
    if request.user.is_authenticated:
        return Cart.objects.filter(user=request.user, status="active").first()
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    return Cart.objects.filter(session_key=session_key, status="active").first()


def cart_context(request):
    """Provide the cart object and item count for authenticated and guest users."""
    cart = get_cart(request)
    # cart_item_count = cart.items.count() if cart else 0
    cart_item_count = cart.items.all().count() if cart else 0
    return {
        "cart": cart,
        "cart_items_count": cart_item_count,
    }

