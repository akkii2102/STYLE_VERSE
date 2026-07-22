"""
URL configuration for shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from shopapp.admin_custome import CustomerAdminSite, SuperAdminSite

# ── Replace the default Django admin site with SuperAdminSite ──────────────
# This means /admin/ requires is_superuser = True
# Sellers (is_staff only) CANNOT access /admin/
# Superusers CAN access both /admin/ and /admin-panel/
admin.site.__class__ = SuperAdminSite
admin.site.site_header = 'STYLEVERSE Super Admin'
admin.site.site_title  = 'STYLEVERSE Super Admin'
admin.site.index_title = 'Super Admin Dashboard'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-panel/', include('subshop.urls')),
    path('seller/', include('subshop.urls')),
    path('', include('shopapp.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)






########    In urls.py   ########

# from django.contrib.auth import views as auth_views

#     path('login',views.login_user, name='login'),
#     path('logout_user',views.logout_user, name='logout'),
#     path('register',views.register_user, name='register'),
#     path('profile_user',views.profile_user, name='profile'),
#     path('edit_profile_user',views.edit_profile, name='edit_profile_user'),
#     path('change_password/', views.change_password, name='change_password'),
#     path('reset_password/', 
#          auth_views.PasswordResetView.as_view(template_name="password_reset.html"), 
#          name="reset_password"),
#     path('reset_password_sent/', 
#          auth_views.PasswordResetDoneView.as_view(template_name="password_reset_sent.html"), 
#          name="password_reset_done"),
#     path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
#     path('reset_password_complete/', 
#          auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), 
#          name="password_reset_complete"),