from django.contrib import admin


# ──────────────────────────────────────────────────────────
#  SUPERADMIN SITE  →  /admin/
#  Only users with is_superuser = True can access this.
#  Sellers (is_staff only) are blocked here.
# ──────────────────────────────────────────────────────────
class SuperAdminSite(admin.AdminSite):
    site_header = 'STYLEVERSE Super Admin'
    site_title  = 'STYLEVERSE Super Admin'
    index_title = 'Super Admin Dashboard'

    def has_permission(self, request):
        """Only superusers (not just staff) can access /admin/"""
        return request.user.is_active and request.user.is_superuser


# ──────────────────────────────────────────────────────────
#  CUSTOMER / SELLER ADMIN SITE  (legacy, kept for compat)
# ──────────────────────────────────────────────────────────
class CustomerAdminSite(admin.AdminSite):
    site_header = 'Customer Management Portal'
    site_title  = 'Customer Admin'
    index_title = 'Welcome to the Customer Portal'

    def has_permission(self, request):
        return request.user.is_active and request.user.is_staff
