import json

import openpyxl
import pandas as pd
from decimal import Decimal
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Product, Wishlist, WishlistItem, Cart, Wishlist, Contribution, ProductImage, Tag, ProductVariant, \
    Category
from django.contrib.auth.models import User
from .wishlist import WishlistService
from django.db.models import Q, Count
from django.utils import timezone
from .forms import ProductForm, InventoryProductForm, FeaturedAndAvailableForm, CategoryForm, BulkCategoryUploadForm, \
    BulkProductUploadForm


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
    Search products and their variants based on query terms.
    - Rank results by relevance: Product title and description matches are prioritized.
    """
    query = request.GET.get('q', '').strip()  # Get search terms from query parameter
    products = Product.objects.none()  # Default empty queryset

    if query:
        search_terms = query.split()

        title_q = Q()
        description_q = Q()
        other_q = Q()

        for term in search_terms:
            title_q |= Q(name__icontains=term)
            description_q |= Q(description__icontains=term)
            other_q |= Q(category__name__icontains=term) | Q(tags__name__icontains=term) | Q(variants__color__icontains=term) | Q(variants__size__icontains=term)

        products = Product.objects.filter(
            title_q | description_q | other_q
        ).distinct().annotate(
            relevance=Count('name', filter=title_q) * 3 + Count('description', filter=description_q) * 2 + Count('category', filter=other_q)
        ).order_by('-relevance', 'name')

    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'synergy_mall/search_results.html', context)


@user_passes_test(is_vendor)  # Restrict access to vendors only
def add_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)

        if product_form.is_valid():
            # Save the product but don't commit yet (because we need to assign the vendor)
            product = product_form.save(commit=False)
            product.vendor = request.user  # Assign the current user as the vendor
            product.save()

            # Handle multiple images
            images = request.FILES.getlist('images')
            for image in images:
                ProductImage.objects.create(product=product, image=image)

            # Handle product variants (colors and sizes)
            colors = product_form.cleaned_data['colors']  # This will be a list of colors (or empty)
            sizes = product_form.cleaned_data['sizes']  # This will be a list of sizes (or empty)

            if colors or sizes:  # Create variants only if colors or sizes are provided
                for color in colors or [None]:  # If no colors, use None
                    for size in sizes or [None]:  # If no sizes, use None
                        ProductVariant.objects.create(product=product, color=color, size=size)

            messages.success(request, 'Product and variants added successfully!')
            return redirect('product_list')
    else:
        product_form = ProductForm()

    return render(request, 'synergy_mall/add_product.html', {'form': product_form})


@user_passes_test(is_vendor)
def bulk_add_products(request):
    if request.method == 'POST':
        form = BulkProductUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']

            try:
                # Load the Excel file using pandas
                df = pd.read_excel(excel_file, engine='openpyxl')

                # Validate and process each row
                for index, row in df.iterrows():
                    product_name = row['Name']
                    description = row['Description']
                    category_name = row['Category']
                    price = row['Price']
                    sale_price = row.get('Sale Price', None)  # Sale price is optional
                    color = row.get('Color', None)
                    size = row.get('Size', None)
                    sku = row['SKU']
                    stock = row['Stock']

                    # Get or create the category
                    category, created = Category.objects.get_or_create(name=category_name)

                    # Create the product (if it doesn't already exist)
                    product, created = Product.objects.get_or_create(
                        name=product_name,
                        description=description,
                        price=price,
                        sale_price=sale_price,
                        vendor=request.user,  # Assign the current user as the vendor
                        category=category,
                    )

                    # Create the variant (color and size can be None if not specified)
                    ProductVariant.objects.create(
                        product=product,
                        color=color,
                        size=size,
                        sku=sku,
                        stock=stock,
                    )

                messages.success(request, 'Products added successfully!')
                return redirect('product_list')

            except Exception as e:
                messages.error(request, f'Error processing file: {e}')
    else:
        form = BulkProductUploadForm()

    return render(request, 'synergy_mall/bulk_add_products.html', {'form': form})


def download_bulk_product_template(request):
    # Create a new Excel workbook and sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Product Template"

    # Define the headers (columns) for the Excel file
    headers = [
        'Name', 'Description', 'Category', 'Price', 'Sale Price (Optional)', 'Color (Optional)',
        'Size (Optional)', 'SKU', 'Stock'
    ]

    # Add the headers to the first row
    for col_num, header in enumerate(headers, 1):
        ws.cell(row=1, column=col_num, value=header)

    # Get all available categories from the database
    categories = Category.objects.values_list('name', flat=True)

    # Create a separate sheet for categories
    category_sheet = wb.create_sheet(title="Categories")
    for index, category in enumerate(categories, 1):
        category_sheet.cell(row=index, column=1, value=category)

    # Define the data validation for category dropdown
    category_range = f'Categories!$A$1:$A${len(categories)}'  # Adjust the range based on the number of categories
    category_validation = openpyxl.worksheet.datavalidation.DataValidation(
        type="list", formula1=category_range, allow_blank=False
    )

    # Apply the validation to the category column (column 3)
    category_validation.add(f'C2:C1048576')  # Excel's max row limit for validation

    ws.add_data_validation(category_validation)

    # Set the response to return the Excel file as an attachment
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    # Define the filename for the Excel file
    filename = f'bulk_product_template_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename={filename}'

    # Save the workbook to the response
    wb.save(response)

    return response


@user_passes_test(is_vendor)
def upload_product_images(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user)

    if request.method == 'POST':
        images = request.FILES.getlist('images')
        for image in images:
            ProductImage.objects.create(product=product, image=image)
        messages.success(request, 'Images uploaded successfully!')
        return redirect('product_list')

    return render(request, 'synergy_mall/upload_images.html', {'product': product})


def view_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variants = product.variants.all()

    # Group variants by available colors and sizes
    available_colors = variants.values_list('color', flat=True).distinct()
    available_sizes = variants.values_list('size', flat=True).distinct()

    context = {
        'product': product,
        'variants': variants,
        'available_colors': available_colors,
        'available_sizes': available_sizes,
    }
    return render(request, 'synergy_mall/view_product.html', context)


# @user_passes_test(is_vendor)
# def edit_product(request, product_id):
#     product = get_object_or_404(Product, id=product_id, vendor=request.user)
#
#     if request.method == 'POST':
#         form = InventoryProductForm(request.POST, request.FILES, instance=product)
#         if form.is_valid():
#             product = form.save(commit=False)
#             product.save()
#
#             # Process the tags input
#             tags_input = request.POST.get('tags')
#             if tags_input:
#                 tag_names = [tag.strip() for tag in tags_input.split(',')]
#                 product.tags.set(Tag.objects.filter(name__in=tag_names))
#
#             # Update the variants (colors, sizes) if provided
#             colors = form.cleaned_data['colors']  # List of colors (can be empty)
#             sizes = form.cleaned_data['sizes']  # List of sizes (can be empty)
#
#             # Clear existing variants and recreate only if colors or sizes are provided
#             product.variants.all().delete()
#
#             if colors or sizes:
#                 for color in colors:
#                     for size in sizes:
#                         ProductVariant.objects.create(product=product, color=color, size=size)
#
#             messages.success(request, 'Product and variants updated successfully!')
#             return redirect('product_list')
#     else:
#         form = InventoryProductForm(instance=product)
#
#     return render(request, 'synergy_mall/edit_product.html', {'form': form, 'product': product})

@user_passes_test(is_vendor)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user)

    if request.method == 'POST':
        form = InventoryProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()

            # Process the tags input
            tags_input = request.POST.get('tags')
            if tags_input:
                tag_names = [tag.strip() for tag in tags_input.split(',')]
                product.tags.set(Tag.objects.filter(name__in=tag_names))

            # Handle variants (colors, sizes, SKU, and stock)
            colors = form.cleaned_data['colors']  # Comma-separated string
            sizes = form.cleaned_data['sizes']    # Comma-separated string
            sku = form.cleaned_data.get('sku', None)
            stock = form.cleaned_data.get('stock', None)

            # Convert comma-separated strings into lists
            color_list = [color.strip() for color in colors.split(',')] if colors else []
            size_list = [size.strip() for size in sizes.split(',')] if sizes else []

            # Clear existing variants and recreate them
            product.variants.all().delete()

            for color in color_list:
                for size in size_list:
                    # Generate SKU if not provided
                    if not sku:
                        sku = f"{product.name[:3]}-{color[:2]}-{size[:2]}"  # Example SKU generation logic

                    # Create the variant with the provided SKU and stock
                    ProductVariant.objects.create(
                        product=product,
                        color=color,
                        size=size,
                        sku=sku,
                        stock=stock if stock else 0  # Assign default stock if not provided
                    )

            messages.success(request, 'Product and variants updated successfully!')
            return redirect('product_list')
    else:
        form = InventoryProductForm(instance=product)

    return render(request, 'synergy_mall/edit_product.html', {'form': form, 'product': product})


@user_passes_test(is_vendor)
def remove_product_image(request, product_id, image_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user)
    image = get_object_or_404(ProductImage, id=image_id, product=product)
    image.delete()
    messages.success(request, 'Image removed successfully.')
    return redirect('edit_product', product_id=product_id)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variants = product.variants.all()

    context = {
        'product': product,
        'vendor_profile': product.vendor.vendor_profile,
        'images': product.images.all(),
        'variants': variants,
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


# CATEGORIES VIEW
# @user_passes_test(is_manager)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')  # Redirect to a page showing the list of categories
    else:
        form = CategoryForm()

    return render(request, 'synergy_mall/add_category.html', {'form': form})


def category_list(request):
    categories = Category.objects.all()  # Retrieve all categories from the database
    return render(request, 'synergy_mall/category_list.html', {'categories': categories})


def bulk_category_upload(request):
    if request.method == 'POST':
        form = BulkCategoryUploadForm(request.POST, request.FILES)

        if form.is_valid():
            # Get the uploaded file
            uploaded_file = request.FILES['file']

            # Read the file depending on its extension
            try:
                if uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                elif uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    messages.error(request, 'Unsupported file format. Please upload an Excel or CSV file.')
                    return redirect('bulk_category_upload')

                # Loop through the DataFrame and create categories
                for index, row in df.iterrows():
                    category_name = row.get('name')
                    category_description = row.get('description', '')

                    if category_name:  # Ensure the name is not empty
                        Category.objects.get_or_create(
                            name=category_name,
                            defaults={'description': category_description}
                        )

                messages.success(request, 'Categories uploaded successfully!')
                return redirect('category_list')  # Redirect to the category list page
            except Exception as e:
                messages.error(request, f'Error processing file: {e}')
                return redirect('bulk_category_upload')
    else:
        form = BulkCategoryUploadForm()

    return render(request, 'synergy_mall/bulk_category_upload.html', {'form': form})


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


def add_to_cart(request, product_id):
    variant_id = request.POST.get('variant_id')
    variant = get_object_or_404(ProductVariant, id=variant_id)

    # Add variant to the cart (this will depend on your cart implementation)
    # cart.add(variant=variant, quantity=1)

    return redirect('view_cart')
