from django.contrib import admin


def superadmin_has_permission(request):
    """Only active superusers (is_superuser = True) can access /admin/. Sub-admins are blocked."""
    return bool(request.user and request.user.is_active and request.user.is_superuser)


class SuperAdminSite(admin.AdminSite):
    site_header = 'STYLEVERSE Super Admin'
    site_title  = 'STYLEVERSE Super Admin'
    index_title = 'Super Admin Dashboard'

    def has_permission(self, request):
        return superadmin_has_permission(request)


# Enforce superuser-only access on default admin.site instance
admin.site.has_permission = superadmin_has_permission
admin.site.site_header = 'STYLEVERSE Super Admin'
admin.site.site_title  = 'STYLEVERSE Super Admin'
admin.site.index_title = 'Super Admin Dashboard'


# ──────────────────────────────────────────────────────────
#  CUSTOMER / SELLER ADMIN SITE  (legacy, kept for compat)
# ──────────────────────────────────────────────────────────
class CustomerAdminSite(admin.AdminSite):
    site_header = 'Customer Management Portal'
    site_title  = 'Customer Admin'
    index_title = 'Welcome to the Customer Portal'

    def has_permission(self, request):
        return request.user.is_active and request.user.is_staff
