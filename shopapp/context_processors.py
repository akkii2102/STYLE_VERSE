from shopapp.models import Wishlist, ProductRequest


def cart_context(request):
    """Inject cart_count into every template."""
    cart = request.session.get('cart', {})
    cart_count = sum(item.get('quantity', 0) for item in cart.values())
    return {'cart_count': cart_count}


def wishlist_context(request):
    """Inject wishlist_count into every template."""
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return {'wishlist_count': wishlist_count}


def admin_approval_context(request):
    """Inject pending_approval_count into admin templates."""
    pending_approval_count = 0
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        if request.user.is_superuser:
            pending_approval_count = ProductRequest.objects.filter(status='pending').count()
        else:
            pending_approval_count = ProductRequest.objects.filter(user=request.user, status='pending').count()
    return {'pending_approval_count': pending_approval_count}
