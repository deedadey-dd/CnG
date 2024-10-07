from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('add-product/', views.add_product, name='add_product'),
    # path('add-category/', views.add_category, name='add_category'),
    # path('product-list/', views.product_list, name='product_list'),
    # path('products/suspend/<int:product_id>/', views.suspend_product, name='suspend_product'),
    # path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    # path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    # path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    # path('cart/', views.cart_detail, name='cart_detail'),
    # path('checkout/', views.checkout, name='checkout'),
    path('search/', views.search_product, name='search_product'),
    path('wishlist/create/', views.create_wishlist, name='create_wishlist'),
    path('wishlist/<int:wishlist_id>/edit/', views.edit_wishlist, name='edit_wishlist'),
    path('wishlist/<int:wishlist_id>/delete/', views.delete_wishlist, name='delete_wishlist'),
    path('wishlist/my_wishlists/', views.my_wishlists, name='my_wishlists'),
    # path('wishlist/<int:wishlist_id>/add-item/', views.add_product_to_wishlist, name='add_product_to_wishlist'),
    # path('wishlist/<int:wishlist_id>/add-custom-item/', views.add_custom_item_to_wishlist,
    #      name='add_custom_item_to_wishlist'),
    path('wishlist/<int:wishlist_id>/', views.view_wishlist, name='view_wishlist'),
    # path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/add_ajax/', views.add_to_wishlist_ajax, name='add_to_wishlist_ajax'),
    path('wishlists/', views.all_wishlists, name='all_wishlists'),

]
