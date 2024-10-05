from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Wishlist, WishlistItem, Cart, Wishlist
from django.contrib.auth.models import User
from .wishlist import WishlistService
from django.db.models import Q, Count


# Single Responsibility Principle: Separate logic for paginated product fetching.
def get_paginated_products(request, page_number=1, per_page=12):
    products = Product.objects.filter(is_active=True, available=True)
    paginator = Paginator(products, per_page)
    return paginator.get_page(page_number)


# Open/Closed Principle: Extendable logic for actions based on login state.
def index(request):
    page_number = request.GET.get('page', 1)
    products_page = get_paginated_products(request, page_number)

    context = {
        'products_page': products_page
    }
    return render(request, 'synergy_mall/index.html', context)


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        wishlist_id = request.POST.get('wishlist_id')
        wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
        WishlistItem.objects.create(wishlist=wishlist, product=product)
        messages.success(request, f'{product.name} added to {wishlist.title}')
        return redirect('homepage')
    else:
        # Fetch the user's wishlists
        user_wishlists = Wishlist.objects.filter(user=request.user)
        context = {
            'product': product,
            'wishlists': user_wishlists,
        }
        return render(request, 'store/select_wishlist.html', context)


@login_required
def create_wishlist(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        privacy = request.POST.get('privacy', 'private')
        expiry_date = request.POST.get('expiry_date', None)

        wishlist_service = WishlistService(request.user)
        wishlist = wishlist_service.create_wishlist(
            title=title, description=description, privacy=privacy, expiry_date=expiry_date
        )
        messages.success(request, f'Wishlist "{wishlist.title}" created successfully!')
        return redirect('view_wishlist', wishlist_id=wishlist.id)

    return render(request, 'synergy_mall/create_wishlist.html')


@login_required
def delete_wishlist(request, wishlist_id):
    wishlist_service = WishlistService(request.user)
    wishlist_service.delete_wishlist(wishlist_id)
    messages.success(request, 'Wishlist deleted successfully!')
    return redirect('user_wishlists')


@login_required
def edit_wishlist(request, wishlist_id):
    wishlist_service = WishlistService(request.user)
    wishlist = wishlist_service.get_wishlist(wishlist_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        privacy = request.POST.get('privacy', 'private')
        expiry_date = request.POST.get('expiry_date', None)

        wishlist_service.update_wishlist(
            wishlist_id=wishlist.id,
            title=title,
            description=description,
            privacy=privacy,
            expiry_date=expiry_date
        )
        messages.success(request, f'Wishlist "{wishlist.title}" updated successfully!')
        return redirect('view_wishlist', wishlist_id=wishlist.id)

    context = {
        'wishlist': wishlist
    }
    return render(request, 'synergy_mall/edit_wishlist.html', context)


@login_required
def view_wishlist(request, wishlist_id):
    wishlist_service = WishlistService(request.user)
    wishlist = wishlist_service.get_wishlist(wishlist_id)

    context = {
        'wishlist': wishlist,
        'items': wishlist.items.all()  # Prefetch related wishlist items
    }
    return render(request, 'synergy_mall/view_wishlist.html', context)


@login_required
def my_wishlists(request):
    """
    View to list all the logged-in user's wishlists.
    """
    wishlist_service = WishlistService(request.user)
    wishlists = wishlist_service.get_user_wishlists()

    context = {
        'wishlists': wishlists,
    }
    return render(request, 'synergy_mall/my_wishlists.html', context)


def search_product(request):
    """
    Search products based on query terms. Rank results by relevance:
    - Product title matches are prioritized
    - Then description matches
    - Finally, other fields (like tags or category)
    """
    query = request.GET.get('q', '').strip()  # Get search terms from query parameter
    products = Product.objects.none()  # Default empty queryset

    if query:
        # Split the query into individual terms (e.g., handling multi-word queries)
        search_terms = query.split()

        # Build a Q object for searching the title, description, and other fields
        title_q = Q()
        description_q = Q()
        other_q = Q()

        # Iterate over search terms and construct Q objects
        for term in search_terms:
            title_q |= Q(name__icontains=term)
            description_q |= Q(description__icontains=term)
            other_q |= Q(category__name__icontains=term) | Q(tags__name__icontains=term)

        # Apply the search queries, prioritizing by relevance
        products = Product.objects.filter(
            title_q | description_q | other_q
        ).annotate(
            # Relevance score: prioritize title matches, then description, then others
            relevance=Count('name', filter=title_q) * 3 + Count('description', filter=description_q) * 2 + Count('category', filter=other_q)
        ).order_by('-relevance', 'name')  # Sort by relevance score first, then alphabetically by name

    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'synergy_mall/search_results.html', context)

