from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add-product/', views.add_product, name='add_product'),
    path('add-product-bulk/', views.bulk_add_products, name='add_bulk_product'),
    path('add-product/', views.upload_product_images, name='upload_product_images'),
    path('add-category/', views.add_category, name='add_category'),
    path('product-list/', views.product_list, name='product_list'),
    path('products/suspend/<int:product_id>/', views.suspend_product, name='suspend_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/variants/<int:product_id>/', views.manage_product_variants, name='manage_product_variants'),
    path('products/remove-image/<int:product_id>/<int:image_id>/', views.remove_product_image, name='remove_product_image'),
    path('download-template/', views.download_bulk_product_template, name='download_bulk_product_template'),
    # path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    # path('cart/', views.cart_detail, name='cart_detail'),
    # path('checkout/', views.checkout, name='checkout'),

    # Cart URLs
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/items/', views.get_cart_items, name='get_cart_items'),


    # Order URLs
    path('orders/', views.view_orders, name='view_orders'),
    path('orders/create/', views.create_order, name='create_order'),

    path('search/', views.search_product, name='search_product'),
    path('wishlist/create/', views.create_wishlist, name='create_wishlist'),
    path('wishlist/<int:wishlist_id>/edit/', views.edit_wishlist, name='edit_wishlist'),
    path('wishlist/<int:wishlist_id>/delete/', views.delete_wishlist, name='delete_wishlist'),
    path('wishlist/my_wishlists/', views.my_wishlists, name='my_wishlists'),
    path('wishlist/<int:wishlist_id>/item/<int:item_id>/update/', views.update_wishlist_item,
         name='update_wishlist_item'),
    path('wishlist/<int:wishlist_id>/item/<int:item_id>/remove/', views.remove_wishlist_item,
         name='remove_wishlist_item'),
    path('wishlist/<int:wishlist_id>/', views.view_wishlist, name='view_wishlist'),
    # path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/add_ajax/', views.add_to_wishlist_ajax, name='add_to_wishlist_ajax'),
    path('wishlist/update_order/', views.update_wishlist_order, name='update_wishlist_order'),
    path('wishlists/', views.all_wishlists, name='all_wishlists'),
    path('wishlist/<int:wishlist_id>/contribute/', views.contribute_to_wishlist, name='contribute_to_wishlist'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add', views.add_category, name='add_category'),
    path('bulk-upload-categories/', views.bulk_category_upload, name='bulk_category_upload'),
    path('vendor/<int:vendor_id>/products/', views.vendor_products, name='vendor_products'),
    path('fetch-receiver-wishlists/', views.fetch_receiver_wishlists, name='fetch_receiver_wishlists'),
    path('process-gift-payment/<int:product_id>/', views.process_gift_payment, name='process_gift_payment'),
    path('gifts/received/', views.received_gifts, name='received_gifts'),
]
