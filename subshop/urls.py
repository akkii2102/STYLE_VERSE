from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_index, name='admin_index'),
    path('login/', views.admin_login, name='admin_login'),
    path('orders/', views.admin_orders, name='admin_orders'),
    path('products/', views.admin_products, name='admin_products'),
    path('people/', views.admin_people, name='admin_people'),
    path('messages/', views.admin_messages_view, name='admin_messages'),
    path('discussions/', views.admin_discussions_view, name='admin_discussions'),
    path('invoice/<int:order_id>/', views.admin_invoice, name='admin_invoice'),
]
