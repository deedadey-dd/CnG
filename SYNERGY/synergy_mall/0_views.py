import random
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from datetime import datetime

from users.models import Vendor
from .forms import ProductForm, CategoryForm, InventoryProductForm, FeaturedAndAvailableForm, WishlistForm, \
    WishlistItemForm, CustomItemForm, UpdateExpiryDateForm
from .models import Product, Category, Tag, Cart, CartItem, Order, Wishlist, WishlistItem, ProductImage, User

CARD_COLORS = ['3FA2F6', 'FF4191', '36BA98', '597445', 'E0A75E', 'FF6969', '06D001', '83B4FF', 'C738BD',
               'A1DD70', 'D2649A', '40A578', 'FF76CE', 'AF8260', '41B06E', '5755FE', ]


# Helper function to check if user is vendor
def is_vendor(user):
    return user.is_authenticated and (user.role == 'vendor')  # Check if user is admin or vendor


def is_manager(user):
    return user.is_authenticated and user.groups.filter(name='Managers').exists()


def index(request):
    query = request.GET.get('search', '')  # Get the search term from the query parameters
    products = Product.objects.filter(is_active=True, available=True).order_by('-id')  # Fetch active and available products, ordered by most recent

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    paginator = Paginator(products, 20)  # Paginate with 20 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  # Get the products for the current page

    return render(request, 'synergy_mall/index.html', {'page_obj': page_obj, 'query': query})


def search_product(request):
    query = request.GET.get('q', '')  # Get the search query
    category_filter = request.GET.get('category', '')
    condition_filter = request.GET.get('condition', '')
    vendor_filter = request.GET.get('vendor', '')
    print(f'query={query}, cat={category_filter}, condiiton={condition_filter}, vendor={vendor_filter}')
    # Start with all active products
    products = Product.objects.filter(is_active=True)

    # Search logic: match query with product name, description, or tags
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__name__icontains=query)  # Tags field is a ManyToManyField
        ).distinct()

    # Filter by category
    if category_filter:
        products = products.filter(category__id=category_filter)

    # Filter by condition
    if condition_filter:
        products = products.filter(condition=condition_filter)

    # Filter by vendor
    if vendor_filter:
        products = products.filter(vendor__id=vendor_filter)

    # Pass the query and filters to the template for reuse in the search bar
    categories = Category.objects.all()  # Get all categories for the filter dropdown
    vendors = Product.objects.values('vendor').distinct()  # Get distinct vendors
    context = {
        'products': products,
        'query': query,
        'categories': categories,
        'vendors': vendors,
        'selected_category': category_filter,
        'selected_condition': condition_filter,
        'selected_vendor': vendor_filter,
    }
    return render(request, 'synergy_mall/index.html', context)


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


# ## CART FEATURE ##

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = request.POST.get('quantity', 1)

    # Get or create a cart for the user or session
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)

    # Check if the item is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += int(quantity)
    cart_item.save()

    messages.success(request, f'{product.name} added to cart.')
    return redirect('cart_detail')  # Redirect to the cart view


def cart_detail(request):
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
    else:
        cart = Cart.objects.get(session_key=request.session.session_key)

    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.get_total_price() for item in cart_items)

    return render(request, 'synergy_mall/cart_detail.html', {'cart_items': cart_items, 'total_price': total_price})


def checkout(request):
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
    else:
        return redirect('login')  # Redirect non-logged-in users to the login page

    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart_detail')

    # Create an order for each cart item
    for item in cart_items:
        order = Order.objects.create(
            user=request.user,
            product=item.product,
            quantity=item.quantity,
            total_price=item.get_total_price(),
            status='pending',
        )
        # Reduce stock from the product
        item.product.stock -= item.quantity
        item.product.save()

    # Clear the cart after checkout
    cart_items.delete()

    messages.success(request, 'Order placed successfully!')
    return redirect('order_summary')


# ## WISHLIST VIEWS ##

@login_required
def create_wishlist(request):
    if request.method == 'POST':
        form = WishlistForm(request.POST)
        if form.is_valid():
            wishlist = form.save(commit=False)
            wishlist.user = request.user
            wishlist.save()
            messages.success(request, 'Wishlist created successfully!')
            return redirect('view_wishlist', wishlist_id=wishlist.id)
    else:
        form = WishlistForm()
    return render(request, 'synergy_mall/create_wishlist.html', {'form': form})


def product_list(request):
    products = Product.objects.filter(is_active=True)

    # Filter wishlists that are not expired
    wishlists = Wishlist.objects.filter(user=request.user, expiry_date__gt=timezone.now())

    return render(request, 'product_list.html', {
        'products': products,
        'wishlists': wishlists
    })


def add_product_to_wishlist(request, wishlist_id, product_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    wishlists = get_object_or_404(Wishlist, user=request.user)

    # Check if the product is already in the wishlist
    wishlist_item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product,
        defaults={'quantity': 1}  # Add default quantity if creating a new item
    )

    if not created:
        # If the item already exists, just increase the quantity
        wishlist_item.quantity += 1
        wishlist_item.save()

    # Redirect to the view_wishlist page after successful addition
    return redirect('view_wishlist', wishlist_id=wishlist.id)


def get_receiver_wishlists(request):
    receiver_info = request.GET.get('receiver_info')

    if not receiver_info:
        return JsonResponse({'success': False, 'message': 'No username or phone number provided.'})

    # Try to find the user by username or phone number
    try:
        user = User.objects.get(username=receiver_info)
        print(f"User found by username: {user}")  # Debugging
    except User.DoesNotExist:
        try:
            user = User.objects.get(phone_number=receiver_info)
            print(f"User found by phone number: {user}")  # Debugging
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found.'})

    # Fetch non-expired wishlists for the found user
    wishlists = Wishlist.objects.filter(user=user, expiry_date__gt=timezone.now())
    print(f"Wishlists found: {wishlists}")  # Debugging

    # Prepare wishlists for JSON response
    wishlist_data = [{'id': wishlist.id, 'title': wishlist.title} for wishlist in wishlists]

    return JsonResponse({'success': True, 'wishlists': wishlist_data})


@login_required
def add_custom_item_to_wishlist(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    if wishlist.custom_items.count() >= 2:
        messages.error(request, 'You can only add up to 2 custom items.')
        return redirect('view_wishlist', wishlist_id=wishlist.id)

    if request.method == 'POST':
        form = CustomItemForm(request.POST)
        if form.is_valid():
            custom_item = form.save(commit=False)
            custom_item.wishlist = wishlist
            custom_item.save()
            messages.success(request, 'Custom item added to wishlist!')
            return redirect('view_wishlist', wishlist_id=wishlist.id)
    else:
        form = CustomItemForm()
    return render(request, 'synergy_mall/add_custom_item_to_wishlist.html', {'form': form, 'wishlist': wishlist})


@login_required()
def my_wishlists(request):
    # Ensure user is authenticated
    if not request.user.is_authenticated:
        return redirect('login')

    # Fetch active wishlists for the current user
    wishlists = Wishlist.objects.filter(user=request.user)

    # Prepare wishlists with financial summary and random colors
    wishlists_with_colors = []
    for wishlist in wishlists:
        items = WishlistItem.objects.filter(wishlist=wishlist).all()
        items_summary = items[:5]  # First 5 items
        wishlist.total_price = sum(item.price for item in items)

        # Random color for each card
        # color = CARD_COLORS[len(wishlists_with_colors) % len(CARD_COLORS)]
        color = random.choice(CARD_COLORS)

        wishlists_with_colors.append({
            'wishlist': wishlist,
            'items_summary': items_summary,
            'total_price': wishlist.total_price,
            'color': color
        })

    # Pass data to the template
    context = {
        'wishlists_with_colors': wishlists_with_colors
    }
    return render(request, 'synergy_mall/my_wishlists.html', context)


@login_required
def view_wishlist(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id)
    today = datetime.today().date()
    print(today)
    print(wishlist.expiry_date.date())
    wishlist.days_left = (wishlist.expiry_date.date() - today).days

    return render(request, 'synergy_mall/view_wishlist.html', {'wishlist': wishlist})


@login_required
def update_wishlist_expiry(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id)

    # Check if the logged-in user is the owner of the wishlist
    if wishlist.user != request.user:
        messages.error(request, "You are not authorized to update this wishlist.")
        return redirect('view_wishlist', wishlist_id=wishlist.id)

    if request.method == 'POST':
        # Get the new expiry date and privacy from the form submission
        expiry_date_str = request.POST.get('expiry_date')
        privacy = request.POST.get('privacy')  # Get the privacy value

        if expiry_date_str:
            try:
                # Convert the string to a datetime object
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
                wishlist.expiry_date = expiry_date
                wishlist.privacy = privacy  # Update the privacy field
                wishlist.save()
                messages.success(request, 'Expiry date and privacy settings updated successfully!')
            except ValueError:
                messages.error(request, 'Invalid date format. Please enter a valid date.')
        else:
            messages.error(request, 'Expiry date is required.')

        return redirect('view_wishlist', wishlist_id=wishlist.id)

    return render(request, 'synergy_mall/view_wishlist.html', {'wishlist': wishlist})




#  # Add categories to the db
# def add_category(request):
#     product_categories = [
#         "Electronics", "Phones & Accessories", "Laptops & Computers",
#         "Cameras & Photography", "Headphones & Earbuds",
#         "Wearable Technology", "TVs & Audio",
#         "Video Games & Accessories", "Smart Home Devices",
#         "Home Appliances", "Kitchen Appliances", "Vacuum Cleaners & Floor Care",
#         "Furniture", "Bedding & Bath", "Lighting & Lamps", "Home Decor",
#         "Carpets & Rugs", "Garden Tools & Supplies",
#         "Office Supplies", "Printers & Scanners", "Stationery",
#         "Books", "Magazines & Subscriptions", "Music & CDs", "Movies & DVDs",
#         "Toys & Games", "Action Figures & Collectibles", "Toys", "Puzzles & Board Games",
#         "Baby Products", "Health & Personal Care", "Makeup & Cosmetics", "Fragrances",
#         "Men's Grooming", "Fitness Equipment", "Sports & Outdoors", "Camping & Hiking",
#         "Cycling", "Fishing & Hunting", "Pet Supplies", "Men's Clothing", "Women's Clothing",
#         "Jewelry", "Handbags & Wallets", "Sunglasses & Eyewear", "Watches", "Footwear", "Underwear & Lingerie",
#         "Children's Clothing", "School Supplies", "Backpacks & Bags", "Groceries",
#         "Snacks & Beverages", "Pantry Staples", "Food", "Organic Products",
#         "Wine & Spirits", "Tools & Hardware", "Paint & Wallpaper",
#         "Plumbing Supplies", "Electrical Supplies", "Automotive", "Car Electronics",
#         "Car Care", "Motorcycle Gear", "Batteries & Chargers",
#         "Travel Accessories", "Luggage & Suitcases",
#     ]
#
#     sorted_categories = sorted(product_categories)
#
#     for category_name in sorted_categories:
#         Category.objects.get_or_create(name=category_name)
#         print(category_name)

