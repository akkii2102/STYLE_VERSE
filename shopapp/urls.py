from django.urls import path
from . import views

from django.contrib.auth import views as auth_views


urlpatterns = [
    # ── Public pages ──────────────────────────────────────
    path('', views.index, name='index'),
    path('details/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('search/', views.search, name='search'),
    path('men/', views.men, name='men'),
    path('women/', views.women, name='women'),

    # ── Auth ──────────────────────────────────────────────
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('forgotpassword/', views.forgotpassword, name='forgotpassword'),

    # ── User account ──────────────────────────────────────
    path('profile/', views.editprofile, name='editprofile'),
    path('changepassword/', views.changepassword, name='changepassword'),

    # ── Shop flow ─────────────────────────────────────────
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/', views.order, name='order'),
    path('orders/', views.order, name='orders'),          # alias
    path('invoice/<int:order_id>/', views.invoice, name='invoice'),

    # ── Wishlist ──────────────────────────────────────────
    path('wishlist/', views.wishlist, name='wishlist'),
    path('toggle-wishlist/', views.toggle_wishlist, name='toggle_wishlist'),

    # ── Misc ──────────────────────────────────────────────
    path('cards/', views.card, name='card'),
]
