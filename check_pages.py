"""
Quick page health check — runs against the test client (no server needed).
Tests every public URL in the project for HTTP 200 / expected redirects.
Run:  python check_pages.py
"""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from shopapp.models import Product, Men, Women, Order, ProductReview

client = Client()

OK   = '\033[92m✓\033[0m'
FAIL = '\033[91m✗\033[0m'
WARN = '\033[93m~\033[0m'

results = []

def check(label, url, expected=(200,), method='GET', data=None, client_obj=None):
    c = client_obj or client
    try:
        if method == 'POST':
            resp = c.post(url, data or {})
        else:
            resp = c.get(url)
        status = resp.status_code
        ok = status in expected
        sym = OK if ok else FAIL
        results.append((ok, label, url, status))
        print(f'  {sym}  [{status}]  {label}  ({url})')
    except Exception as e:
        results.append((False, label, url, f'ERROR: {e}'))
        print(f'  {FAIL}  [ERR]  {label}  ({url})  → {e}')

print('\n' + '═'*60)
print('  STYLEVERSE — Page Health Check')
print('═'*60)

# ── Public pages ────────────────────────────────────────────
print('\n[PUBLIC PAGES]')
check('Homepage',           '/')
check('Shop All / New Arr', '/details/')
check('Men Category',       '/men/')
check('Women Category',     '/women/')
check('About Us',           '/about/')
check('Contact',            '/contact/')
check('Search (empty)',     '/search/')
check('Search (query)',     '/search/?q=shirt')
check('Login page',         '/login/')
check('Register page',      '/register/')
check('Forgot Password',    '/forgotpassword/')

# ── Product detail pages ─────────────────────────────────────
print('\n[PRODUCT DETAIL PAGES]')
p = Product.objects.first()
m = Men.objects.first()
w = Women.objects.first()
if p:
    check(f'Product detail (id={p.pk})',  f'/product/{p.pk}/')
    check(f'Product detail ?type=product',f'/product/{p.pk}/?type=product')
if m:
    check(f'Men product detail (id={m.pk})', f'/product/{m.pk}/?type=men')
if w:
    check(f'Women product detail (id={w.pk})', f'/product/{w.pk}/?type=women')

# ── Brand filter pages ────────────────────────────────────────
print('\n[BRAND FILTER PAGES]')
check('Shop All → brand=nike',     '/details/?brand=nike')
check('Shop All → brand=zara',     '/details/?brand=zara')
check('Men → brand=nike',          '/men/?brand=nike')
check('Women → brand=zara',        '/women/?brand=zara')
check('Shop All → price 0-500',    '/details/?price_range=0-500')
check('Men → price 5000-plus',     '/men/?price_range=5000-plus')

# ── Auth-required pages (should redirect to login) ───────────
print('\n[AUTH REQUIRED PAGES — expect redirect 302]')
check('Cart (unauth)',       '/cart/',       expected=(200, 302))
check('Checkout (unauth)',   '/checkout/',   expected=(302,))
check('Orders (unauth)',     '/orders/',     expected=(302,))
check('Wishlist (unauth)',   '/wishlist/',   expected=(302,))
check('Profile (unauth)',    '/profile/',    expected=(302,))
check('Change pwd (unauth)', '/changepassword/', expected=(302,))

# ── Create a test user and check auth pages ───────────────────
print('\n[AUTH REQUIRED PAGES — logged in as regular user]')
test_user, _ = User.objects.get_or_create(username='_healthcheck_user_')
test_user.set_password('testpass123')
test_user.save()
auth_client = Client()
auth_client.login(username='_healthcheck_user_', password='testpass123')

check('Cart (auth)',        '/cart/',       client_obj=auth_client)
check('Checkout (auth)',    '/checkout/',   client_obj=auth_client)
check('Orders (auth)',      '/orders/',     client_obj=auth_client)
check('Wishlist (auth)',    '/wishlist/',   client_obj=auth_client)
check('Profile (auth)',     '/profile/',    client_obj=auth_client)
check('Change pwd (auth)',  '/changepassword/', client_obj=auth_client)

# ── Seller / Sub-admin pages ──────────────────────────────────
print('\n[SELLER / ADMIN PAGES]')
check('Seller login',       '/seller/login/')
check('Admin panel login',  '/admin-panel/login/')

# ── Seller login as staff user ────────────────────────────────
print('\n[SELLER PANEL — logged in as staff]')
staff_user, _ = User.objects.get_or_create(username='_healthcheck_staff_')
staff_user.set_password('testpass123')
staff_user.is_staff = True
staff_user.save()
staff_client = Client()
staff_client.login(username='_healthcheck_staff_', password='testpass123')

check('Admin index',        '/seller/',            client_obj=staff_client)
check('Admin products',     '/seller/products/',   client_obj=staff_client)
check('Admin orders',       '/seller/orders/',     client_obj=staff_client)
check('Admin messages',     '/seller/messages/',   client_obj=staff_client)
check('Admin discussions',  '/seller/discussions/',client_obj=staff_client)
check('Admin delivery',     '/seller/delivery/',   client_obj=staff_client)
check('Admin stock',        '/seller/stock/',      client_obj=staff_client)
check('Admin profile',      '/seller/profile/',    client_obj=staff_client)

# ── Order invoice (need an order belonging to the test user) ─
print('\n[ORDER / INVOICE]')
from django.contrib.auth.models import User as _User
order = Order.objects.first()
if order:
    # Log in as the order's actual owner to test invoice
    inv_client = Client()
    inv_client.force_login(order.user)
    check(f'Invoice (owner, order {order.pk})', f'/invoice/{order.pk}/',
          expected=(200,), client_obj=inv_client)

# ── Static assets exist ───────────────────────────────────────
print('\n[STATIC FILES CHECK]')
import os
static_files = [
    'static/css/styleverse.css',
    'static/css/list.css',
    'static/css/contact.css',
    'static/images/hero1.png',
    'static/images/hero2.png',
    'static/images/hero3.png',
    'static/images/hero4.png',
    'static/images/category_men.png',
    'static/images/category_women.png',
]
for sf in static_files:
    full = os.path.join(os.path.dirname(__file__), sf)
    exists = os.path.exists(full)
    sym = OK if exists else FAIL
    results.append((exists, sf, sf, 'exists' if exists else 'MISSING'))
    print(f'  {sym}  {sf}')

# ── Template files exist ─────────────────────────────────────
print('\n[TEMPLATE FILES CHECK]')
templates = [
    'templates/index.html',
    'templates/base.html',
    'templates/about_us.html',
    'templates/contact_us.html',
    'templates/cart.html',
    'templates/checkout.html',
    'templates/orders.html',
    'templates/invoice.html',
    'templates/wishlist.html',
    'templates/search.html',
    'templates/products/product_list.html',
    'templates/products/product_detail.html',
    'templates/products/product_card.html',
    'templates/mens/men.html',
    'templates/womens/women.html',
    'templates/login/login.html',
    'templates/login/register.html',
    'templates/login/forgotpassword.html',
    'templates/login/editprofile.html',
    'templates/login/changepassword.html',
    'templates/partials/header.html',
    'templates/partials/footer.html',
    'templates/sub-admin/dashboard.html',
    'templates/sub-admin/products.html',
    'templates/sub-admin/orders.html',
]
for tf in templates:
    full = os.path.join(os.path.dirname(__file__), tf)
    exists = os.path.exists(full)
    sym = OK if exists else FAIL
    results.append((exists, tf, tf, 'exists' if exists else 'MISSING'))
    print(f'  {sym}  {tf}')

# ── DB record counts ─────────────────────────────────────────
print('\n[DATABASE COUNTS]')
counts = {
    'Products (general)': Product.objects.count(),
    'Men products':        Men.objects.count(),
    'Women products':      Women.objects.count(),
    'Reviews':             ProductReview.objects.count(),
    'Orders':              Order.objects.count(),
    'Users':               User.objects.count(),
}
for k, v in counts.items():
    sym = OK if v > 0 else WARN
    print(f'  {sym}  {k}: {v}')

# ── Summary ──────────────────────────────────────────────────
total  = len(results)
passed = sum(1 for r in results if r[0])
failed = total - passed

print('\n' + '═'*60)
print(f'  RESULTS: {passed}/{total} passed', end='')
if failed:
    print(f'  —  {failed} FAILED:')
    for r in results:
        if not r[0]:
            print(f'      {FAIL}  {r[1]}  [{r[3]}]  {r[2]}')
else:
    print('  — ALL PASSED ✓')
print('═'*60 + '\n')

# Clean up test users
User.objects.filter(username__in=['_healthcheck_user_', '_healthcheck_staff_']).delete()
