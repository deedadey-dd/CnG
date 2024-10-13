import json
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Product, Wishlist, WishlistItem, Cart, Wishlist, Contribution, ProductImage, Tag
from django.contrib.auth.models import User
from .wishlist import WishlistService
from django.db.models import Q, Count
from django.utils import timezone
from .forms import ProductForm, InventoryProductForm, FeaturedAndAvailableForm, CategoryForm


# Helper function to check if user is vendor
def is_vendor(user):
    return user.is_authenticated and (user.role == 'vendor')  # Check if user is admin or vendor


def is_manager(user):
    return user.is_authenticated and user.groups.filter(name='Managers').exists()


# Single Responsibility Principle: Separate logic for paginated product fetching.
def get_paginated_products(request, page_number=1, per_page=12):
    products = Product.objects.filter(is_active=True, available=True)
    paginator = Paginator(products, per_page)
    return paginator.get_page(page_number)


# Open/Closed Principle: Extendable logic for actions based on login state.
def index(request):
    page_number = request.GET.get('page', 1)
    products_page = get_paginated_products(request, page_number)

    # Fetch the user's non-expired wishlists (if logged in)
    wishlists = Wishlist.objects.not_expired().filter(user=request.user) if request.user.is_authenticated else []

    context = {
        'products_page': products_page,
        'wishlists': wishlists  # Pass the user's wishlists to the template
    }
    return render(request, 'synergy_mall/index.html', context)


@require_POST
@login_required
def add_to_wishlist_ajax(request):
    """
    Handles the AJAX request to add a product to a selected wishlist.
    """
    import json
    data = json.loads(request.body)

    product_id = data.get('product_id')
    wishlist_id = data.get('wishlist_id')

    try:
        product = Product.objects.get(id=product_id)

        # Fetch the user's non-expired wishlists
        wishlist = Wishlist.objects.not_expired().get(id=wishlist_id, user=request.user)

        # Check if the product is already in the wishlist
        wishlist_item, created = WishlistItem.objects.get_or_create(
            wishlist=wishlist,
            product=product
        )

        if created:
            response_data = {
                'success': True,
                'product_name': product.name,
                'wishlist_title': wishlist.title
            }
        else:
            response_data = {
                'success': False,
                'message': 'Product is already in the wishlist.'
            }

    except Product.DoesNotExist:
        response_data = {
            'success': False,
            'message': 'Product not found.'
        }
    except Wishlist.DoesNotExist:
        response_data = {
            'success': False,
            'message': 'Wishlist not found, does not belong to you, or is expired.'
        }

    return JsonResponse(response_data)


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


# @login_required
def view_wishlist(request, wishlist_id):
    wishlist_service = WishlistService(request.user)
    wishlist = wishlist_service.get_wishlist(wishlist_id)

    general_contributions = wishlist.contribution_set.filter(wishlist_item__isnull=True)

    user_info = {}
    if request.user.is_authenticated:
        user_info = {
            'first_name': request.user.first_name,
            'surname': request.user.surname,
            'other_names': request.user.other_names,
            'phone_number': request.user.phone_number,
        }

    context = {
        'wishlist': wishlist,
        'items': wishlist.ordered_items(),  # Load items in the correct order
        'general_contributions': general_contributions,  # Pass general contributions to the template
        'user_info': user_info,
    }
    return render(request, 'synergy_mall/view_wishlist.html', context)


@login_required
def update_wishlist_order(request):
    """Update the order of the wishlist items."""
    if request.method == "POST":
        data = json.loads(request.body)
        wishlist_id = data.get('wishlist_id')
        ordered_item_ids = data.get('ordered_item_ids')

        wishlist = Wishlist.objects.get(id=wishlist_id, user=request.user)
        for index, item_id in enumerate(ordered_item_ids):
            WishlistItem.objects.filter(id=item_id, wishlist=wishlist).update(ordering=index)

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def my_wishlists(request):
    """
    View to list all the logged-in user's wishlists.
    """
    wishlist_service = WishlistService(request.user)
    wishlists = wishlist_service.get_user_wishlists()

    # Paginate the wishlists (e.g., 10 per page)
    paginator = Paginator(wishlists, 9)  # Show 9 wishlists per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }

    return render(request, 'synergy_mall/my_wishlists.html', context)


def all_wishlists(request):
    # Fetch all public, non-expired wishlists
    wishlists = Wishlist.objects.public().not_expired()

    # Paginate the wishlists (e.g., 10 per page)
    paginator = Paginator(wishlists, 9)  # Show 9 wishlists per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }

    return render(request, 'synergy_mall/all_wishlists.html', context)


def update_wishlist_item(request, wishlist_id, item_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    item = get_object_or_404(WishlistItem, id=item_id, wishlist=wishlist)

    if request.method == "POST":
        quantity = request.POST.get('quantity')
        if quantity and int(quantity) > 0:
            item.quantity = int(quantity)
            item.save()
    return redirect('view_wishlist', wishlist_id=wishlist.id)


def remove_wishlist_item(request, wishlist_id, item_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    item = get_object_or_404(WishlistItem, id=item_id, wishlist=wishlist)

    # Remove the item from the wishlist
    item.delete()
    return redirect('view_wishlist', wishlist_id=wishlist.id)


# ########## CONTRIBUTION VIEWS ##########


def contribute_to_wishlist(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id)

    try:
        amount = Decimal(request.POST.get('amount'))  # Ensure it's passed as Decimal
    except (TypeError, ValueError):
        messages.error(request, "Invalid contribution amount.")
        return redirect('view_wishlist', wishlist_id=wishlist_id)

    if amount <= 0:
        messages.error(request, "Contribution amount must be greater than zero.")
        return redirect('view_wishlist', wishlist_id=wishlist_id)

    contributor_name = request.POST.get('contributor_name')
    contact_info = request.POST.get('contact_info')
    message = request.POST.get('message', '')  # Optional message
    item_id = request.POST.get('item_id')  # This will be null for general contributions

    if item_id:
        # Specific item contribution
        item = get_object_or_404(WishlistItem, id=item_id, wishlist=wishlist)
        handle_item_contribution(item, amount, contributor_name, contact_info, message)
        messages.success(request, f"Successfully contributed ${amount} to {item.product.name}.")
    else:
        # General contribution, apply to the first item in the wishlist that needs funds
        handle_general_contribution(wishlist, amount, contributor_name, contact_info, message)
        messages.success(request, f"Successfully contributed ${amount} to {wishlist.title}.")

    return redirect('view_wishlist', wishlist_id=wishlist.id)


def handle_item_contribution(item, amount, contributor_name, contact_info, message):
    """Handle specific item contribution and handle surplus if any."""
    remaining = item.amount_remaining()

    if amount <= remaining:
        item.amount_paid += amount
        item.save()
    else:
        surplus = amount - remaining
        item.amount_paid += remaining
        item.save()
        distribute_surplus(item.wishlist, surplus)

    # Log the contribution with additional details
    Contribution.objects.create(
        wishlist_item=item,
        wishlist=item.wishlist,
        contributor_name=contributor_name,
        contact_info=contact_info,
        message=message,
        amount=amount,
        date=timezone.now()
    )


def handle_general_contribution(wishlist, amount, contributor_name, contact_info, message):
    """Handle general contributions and apply to items in the preferred order."""
    items = wishlist.ordered_items()
    for item in items:
        remaining = item.amount_remaining()
        if amount <= remaining:
            item.amount_paid += amount
            item.save()
            amount = Decimal(0)
            break
        else:   # when contribution amount is greater than remaining amount,
            item.amount_paid += remaining
            item.save()
            amount -= remaining

    # If there's any surplus after all items, add it to user's cash_on_hand
    if amount > 0:
        wishlist.user.cash += amount
        wishlist.user.save()

    # Log the contribution with additional details
    Contribution.objects.create(
        wishlist=wishlist,
        contributor_name=contributor_name,
        contact_info=contact_info,
        message=message,
        amount=amount,
        date=timezone.now()
    )


def distribute_surplus(wishlist, surplus):
    """Distribute surplus funds to other items in the wishlist."""
    items = wishlist.ordered_items()
    for item in items:
        if item.amount_remaining() > 0:
            remaining = item.amount_remaining()
            if surplus <= remaining:
                item.amount_paid += surplus
                item.save()
                return
            else:
                surplus -= remaining
                item.amount_paid += remaining
                item.save()

    # If any surplus is left after all items are funded, add to user's cash_on_hand
    if surplus > 0:
        wishlist.user.cash += surplus
        wishlist.user.save()


# ########## PRODUCT VIEWS ##########
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


@user_passes_test(is_vendor)  # Restrict access to vendors or admins
def add_product(request):
    if request.method == 'POST':
        # Handle product form
        product_form = ProductForm(request.POST, request.FILES)

        if product_form.is_valid():
            # Save the product, but don't commit to add the vendor first
            product = product_form.save(commit=False)
            product.vendor = request.user  # Assign the current user as the vendor
            product.save()

            # Handle multiple images
            images = request.FILES.getlist('images')  # 'images' is the name of the file input for multiple files
            for image in images:
                ProductImage.objects.create(product=product, image=image)  # Create and link images to the product

            messages.success(request, 'Product added successfully!')
            return redirect('product_list')
    else:
        product_form = ProductForm()

    return render(request, 'synergy_mall/add_product.html', {
        'form': product_form
    })


@user_passes_test(is_vendor)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user)

    if request.method == 'POST':
        form = InventoryProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)  # Save the product without committing to the database yet

            # Process the tags input
            tags_input = request.POST.get('tags')
            if tags_input:
                tag_names = [tag.strip() for tag in tags_input.split(',')]
                product.tags.set(Tag.objects.filter(name__in=tag_names))  # Update the tags for the product

            # Save the product to the database
            product.save()

            # Assign tags to the product
            tags = []
            for name in tag_names:
                tag, created = Tag.objects.get_or_create(name=name)
                tags.append(tag)
            product.tags.set(tags)  # Update the product's tags

            messages.success(request, 'Product updated successfully!')
            return redirect('product_list')  # Redirect to vendor inventory page
    else:
        form = InventoryProductForm(instance=product)

    return render(request, 'synergy_mall/edit_product.html', {'form': form, 'product': product})


def product_detail(request, product_id):
    # Fetch the product by its id
    product = get_object_or_404(Product, id=product_id)

    # Pass the product to the template
    context = {
        'product': product,
        'vendor_profile': product.vendor.vendor_profile,
        'images': product.images.all(),
    }
    return render(request, 'synergy_mall/product_detail.html', context)


@user_passes_test(is_manager)
def edit_featured_and_available(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = FeaturedAndAvailableForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product featured and availability status updated!')
            return redirect('manager_dashboard')  # Redirect to manager dashboard
    else:
        form = FeaturedAndAvailableForm(instance=product)

    return render(request, 'synergy_mall/edit_featured_and_available.html', {'form': form, 'product': product})


@user_passes_test(is_manager)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')  # Redirect to a page showing the list of categories
    else:
        form = CategoryForm()

    return render(request, 'add_category.html', {'form': form})


@user_passes_test(is_vendor)
def product_list(request):
    # Fetch the products for the logged-in vendor
    vendor = request.user
    products = Product.objects.filter(vendor=vendor)
    return render(request, 'synergy_mall/product_list.html', {'products': products})


@user_passes_test(is_vendor)
def suspend_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user)
    product.available = False
    product.save()
    messages.success(request, 'Product suspended successfully.')
    return redirect('product_list')


@user_passes_test(is_vendor)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('product_list')

    return render(request, 'synergy_mall/delete_product.html', {'product': product})

