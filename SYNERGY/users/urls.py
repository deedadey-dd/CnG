from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('user_register/', views.user_register, name='user_register'),
    path('vendor_register/', views.vendor_register, name='vendor_register'),
    path('vendor_detail/', views.vendor_detail, name='vendor_detail'),
    path('custom_login/', views.custom_login, name='custom_login'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_me_out, name='logout'),
]
