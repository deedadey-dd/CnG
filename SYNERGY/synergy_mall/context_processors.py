from .models import CartItem


def cart_item_count(request):
    if request.user.is_authenticated:
        cart_items_count = CartItem.objects.filter(cart__user=request.user).count()
    else:
        session_key = request.session.session_key
        cart_items_count = CartItem.objects.filter(cart__session_key=session_key).count()

    return {'cart_items_count': cart_items_count}
