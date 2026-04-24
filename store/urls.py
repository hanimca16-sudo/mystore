from django.urls import path
from . import views

urlpatterns = [
    path('',                        views.product_list,    name='product_list'),
    path('product/<int:pk>/',       views.product_detail,  name='product_detail'),
    path('cart/',                   views.cart_view,       name='cart'),
    path('add/<int:pk>/',           views.add_to_cart,     name='add_to_cart'),
    path('checkout/',               views.checkout,        name='checkout'),
    path('register/',               views.register,        name='register'),
    path('become-seller/',          views.become_seller,   name='become_seller'),
    path('seller/dashboard/',       views.seller_dashboard,name='seller_dashboard'),
    path('seller/add/',             views.add_product,     name='add_product'),
    path('seller/delete/<int:pk>/', views.delete_product,  name='delete_product'),
    path('message/<int:pk>/',       views.send_message,    name='send_message'),
    path('inbox/',                  views.inbox,           name='inbox'),
    path('profile/', views.profile, name='profile'),path('reply/<int:pk>/', views.reply_message, name='reply_message'),path('about/',   views.about,   name='about'),
    path('contact/', views.contact, name='contact'),path('order-success/', views.order_success, name='order_success'),]