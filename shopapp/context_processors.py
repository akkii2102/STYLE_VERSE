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


def announcements_context(request):
    """Inject active announcements dynamically into all templates."""
    try:
        from shopapp.models import Announcement
        announcements = list(Announcement.objects.filter(is_active=True).order_by('order', '-created_at'))
        if not announcements:
            announcements = [
                {'icon': 'fa-truck', 'text': 'Free Shipping Over ₹999'},
                {'icon': 'fa-rotate-left', 'text': '30-Day Easy Returns'},
                {'icon': 'fa-shield-halved', 'text': '100% Secure Checkout'},
                {'icon': 'fa-headset', 'text': '24/7 Customer Support'},
                {'icon': 'fa-tag', 'text': 'New Arrivals Every Week'},
                {'icon': 'fa-star', 'text': '50,000+ Happy Customers'},
            ]
    except Exception:
        announcements = [
            {'icon': 'fa-truck', 'text': 'Free Shipping Over ₹999'},
            {'icon': 'fa-rotate-left', 'text': '30-Day Easy Returns'},
            {'icon': 'fa-shield-halved', 'text': '100% Secure Checkout'},
            {'icon': 'fa-headset', 'text': '24/7 Customer Support'},
            {'icon': 'fa-tag', 'text': 'New Arrivals Every Week'},
            {'icon': 'fa-star', 'text': '50,000+ Happy Customers'},
        ]
    return {'announcements': announcements}
