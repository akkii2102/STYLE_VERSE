from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


# ══════════════════════════════════════════════════════════════
#  ROLE DEFINITIONS
# ══════════════════════════════════════════════════════════════
#
#  SUPER ADMIN  (is_superuser = True)
#    ✅ Website (browse, shop, cart, checkout)
#    ✅ Custom Seller Panel  →  /admin-panel/
#    ✅ Django Super Admin   →  /admin/
#    ✅ Everything
#
#  SUB ADMIN  (is_staff = True,  is_superuser = False)
#    ✅ Website (browse, shop, cart, checkout)
#    ✅ Custom Seller Panel  →  /admin-panel/
#    ❌ Django Super Admin   →  /admin/   (BLOCKED)
#    ❌ Nothing else
#
#  NORMAL USER  (is_staff = False,  is_superuser = False)
#    ✅ Website only
#    ❌ /admin-panel/  (BLOCKED)
#    ❌ /admin/        (BLOCKED)
#
# ══════════════════════════════════════════════════════════════


def admin_required(view_func):
    """
    Protects /admin-panel/ views.
    Allows: Sub Admin (is_staff) + Super Admin (is_superuser)
    Blocks:  Normal users
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access the admin panel.')
            return redirect('admin_login')
        # Both sub-admin (is_staff) and super-admin (is_superuser) are allowed
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return wrapper


def superuser_required(view_func):
    """
    Protects views that ONLY super admins can access.
    Blocks both normal users AND sub-admins.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in.')
            return redirect('login')
        if not request.user.is_superuser:
            messages.error(request, 'Access denied. Super Admin privileges required.')
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return wrapper


def is_sub_admin(user):
    """Helper: True if user is a sub-admin (staff but NOT superuser)."""
    return user.is_active and user.is_staff and not user.is_superuser


def is_super_admin(user):
    """Helper: True if user is a superuser."""
    return user.is_active and user.is_superuser


def get_user_role(user):
    """Returns a label for the user's role."""
    if not user.is_authenticated:
        return 'Guest'
    if user.is_superuser:
        return 'Super Admin'
    if user.is_staff:
        return 'Sub Admin'
    return 'Customer'
