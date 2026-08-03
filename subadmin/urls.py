from django.urls import path
from subadmin import views

urlpatterns = [
    path('', views.admin_index, name='admin_index'),
    # Step 1: Enter registered email → receive a one-time login link
    path('login/', views.admin_login_request, name='admin_login'),
    # Step 2: Actual login form — only reachable via the emailed token link
    path('login/<str:token>/', views.admin_login_verify, name='admin_login_verify'),
    path('orders/', views.admin_orders, name='admin_orders'),
    path('products/', views.admin_products, name='admin_products'),
    path('people/', views.admin_people, name='admin_people'),
    path('messages/', views.admin_messages_view, name='admin_messages'),
    path('discussions/', views.admin_discussions_view, name='admin_discussions'),
    path('delivery/', views.admin_delivery, name='admin_delivery'),
    path('stock/', views.admin_stock, name='admin_stock'),
    path('profile/', views.admin_profile, name='admin_profile'),
    path('invoice/<int:order_id>/', views.admin_invoice, name='admin_invoice'),
]

