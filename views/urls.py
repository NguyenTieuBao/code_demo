from django.urls import path
from .views import index, custom_login,register, custom_logout,change_password, forgot_password, password_reset_confirm, mail_success, product_detail, add_to_cart_or_checkout, checkout_view, create_category_view,product_create_update_view, delete_category_view, delete_product_view, order_list_view
urlpatterns = [
    path('', index, name='index'),
    path('login/', custom_login, name='login'),
    path('register/', register, name='register'),
    path('logout/', custom_logout, name='logout'),
    path('changepassword/', change_password, name='changepassword'),
    path('forgot-password/', forgot_password, name='forgot-password'),
    path('reset-password/<uuid:token>/', password_reset_confirm, name='password-reset-confirm'),
    path('mail-success/', mail_success, name='mail_success'),
    path('product/<slug:slug>/', product_detail, name='product_detail'),
    path('add-to-cart-or-checkout/<int:id>/', add_to_cart_or_checkout, name='add_to_cart_or_checkout'),
    path('checkout/', checkout_view, name='checkout'),
    path('create-category/', create_category_view, name='create_category'),
    path('create-category/<int:id>/', create_category_view, name='edit_category'),
    path('delete-category/<int:id>/', delete_category_view, name='delete_category'),
    path('create-product/', product_create_update_view, name='create_product'),
    path('edit/<int:id>/', product_create_update_view, name='edit_product'),
    path('delete/<int:pk>/', delete_product_view, name='delete_product'),
    path('orders/', order_list_view, name='order-list'),
]