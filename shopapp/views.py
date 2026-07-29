from django.shortcuts import render, redirect, get_object_or_404
from shopapp.models import Contact, UserProfile, Product, Men, Women, Wishlist, Order, OrderItem
from shopapp.forms import LoginUserForm, RegisterUserForm, UserProfileForm, CheckoutForm, SubAdminRequestForm
from django.contrib.auth import authenticate, logout, update_session_auth_hash
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


def notify_super_admin_product_request(product_req, request):
    try:
        superusers = User.objects.filter(is_superuser=True, is_active=True)
        emails = [u.email for u in superusers if u.email]
        if not emails:
            emails = [settings.EMAIL_HOST_USER]
        
        subject = f"[STYLEVERSE Approval Required] Product Request: {product_req.name}"
        message = f"""Hello Super Admin,

Sub Admin '{product_req.user.username}' has submitted a product request requiring your approval.

Request Details:
----------------------------------
Request Type: {product_req.get_request_type_display()}
Category    : {product_req.get_category_display()}
Product Name: {product_req.name}
Price       : ₹{product_req.price}
Discount    : {product_req.discount}%
Status      : Pending Approval

Please log in to the Jazzmin Super Admin panel to approve or reject this request:
{request.build_absolute_uri('/admin/shopapp/productrequest/')}

Thank you,
STYLEVERSE Admin System
"""
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=emails,
            fail_silently=True
        )
    except Exception as e:
        print(f"Error sending email: {e}")


# ──────────────────────────────────────────────────────────
#  BASIC PAGES
# ──────────────────────────────────────────────────────────

def get_all_combined_products(sort_by='-pk'):
    """Combines products from Product, Men, and Women models dynamically."""
    p1 = list(Product.objects.all())
    p2 = list(Men.objects.all())
    p3 = list(Women.objects.all())
    all_prods = p1 + p2 + p3
    reverse = sort_by.startswith('-')
    all_prods.sort(key=lambda x: x.pk, reverse=reverse)
    return all_prods


def get_product_by_pk(pk, model_type=None):
    """Dynamically finds a product by PK across Product, Men, and Women models."""
    model_map = {'product': Product, 'men': Men, 'women': Women}
    if model_type and model_type in model_map:
        obj = model_map[model_type].objects.filter(pk=pk).first()
        if obj:
            return obj
    obj = Product.objects.filter(pk=pk).first()
    if obj: return obj
    obj = Men.objects.filter(pk=pk).first()
    if obj: return obj
    obj = Women.objects.filter(pk=pk).first()
    if obj: return obj
    return None


def index(request):
    products = get_all_combined_products('-pk')
    count = len(products)
    new_arrivals  = products[:8]
    best_sellers  = products[4:12] if count > 4 else products
    trending      = products[2:10] if count > 2 else products
    flash_sale    = products[:4]

    men_products   = list(Men.objects.all().order_by('-pk')[:4])
    women_products = list(Women.objects.all().order_by('-pk')[:4])

    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(
            Wishlist.objects.filter(user=request.user).values_list('object_id', flat=True)
        )

    return render(request, 'index.html', {
        'new_arrivals':   new_arrivals,
        'best_sellers':   best_sellers,
        'trending':       trending,
        'flash_sale':     flash_sale,
        'men_products':   men_products,
        'women_products': women_products,
        'wishlist_ids':   wishlist_ids,
    })

def about(request):
    return render(request, 'about_us.html')

def search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        results = list(Product.objects.filter(
            Q(name__icontains=query)
        )) + list(Men.objects.filter(
            Q(name__icontains=query)
        )) + list(Women.objects.filter(
            Q(name__icontains=query)
        ))

    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(
            Wishlist.objects.filter(user=request.user).values_list('object_id', flat=True)
        )

    return render(request, 'search.html', {'query': query, 'results': results, 'wishlist_ids': wishlist_ids})

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('first-name', '')
        surname = request.POST.get('last-name', '')
        email = request.POST.get('email', '')
        message = request.POST.get('message', '')
        Contact.objects.create(Name=name, Surname=surname, Email=email, Message=message)
        messages.success(request, 'Thank you! Your message has been sent.')
    return render(request, 'contact_us.html')


# ──────────────────────────────────────────────────────────
#  PRODUCT PAGES
# ──────────────────────────────────────────────────────────

def product_detail(request, pk):
    model_type = request.GET.get('type')
    product = get_product_by_pk(pk, model_type=model_type)
    if not product:
        product = get_object_or_404(Product, pk=pk)

    all_prods = get_all_combined_products('-pk')
    related = [p for p in all_prods if p.pk != pk][:4]

    # ── Recently Viewed (session-based) ──────────────────
    viewed = request.session.get('recently_viewed', [])
    if pk in viewed:
        viewed.remove(pk)
    viewed.insert(0, pk)
    viewed = viewed[:6]                          # keep last 6
    request.session['recently_viewed'] = viewed

    rv_ids = [i for i in viewed if i != pk]
    recently_viewed = []
    for vid in rv_ids:
        obj = get_product_by_pk(vid)
        if obj:
            recently_viewed.append(obj)

    sku       = f'SV-{product.pk:04d}'
    category  = 'Fashion'
    brand     = 'STYLEVERSE'
    in_stock  = True
    stock_qty = 15

    all_sizes   = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
    all_colors  = [
        {'name': 'Black',   'hex': '#1a1a2e'},
        {'name': 'White',   'hex': '#f5f5f5'},
        {'name': 'Navy',    'hex': '#1e3a5f'},
        {'name': 'Gold',    'hex': '#c0a36e'},
        {'name': 'Red',     'hex': '#e74c3c'},
        {'name': 'Olive',   'hex': '#6b7c32'},
    ]
    sizes  = all_sizes
    colors = all_colors[:4]

    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(
            Wishlist.objects.filter(user=request.user).values_list('object_id', flat=True)
        )

    return render(request, 'products/product_detail.html', {
        'product':        product,
        'related':        related,
        'recently_viewed': recently_viewed,
        'sku':            sku,
        'category':       category,
        'brand':          brand,
        'in_stock':       in_stock,
        'stock_qty':      stock_qty,
        'sizes':          sizes,
        'colors':         colors,
        'wishlist_ids':   wishlist_ids,
    })


def product_list(request):
    sort_by = request.GET.get('sort', '-pk')
    allowed = ['-pk', 'pk', 'price', '-price']
    if sort_by not in allowed:
        sort_by = '-pk'
    products = get_all_combined_products(sort_by)
    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(
            Wishlist.objects.filter(user=request.user).values_list('object_id', flat=True)
        )
    return render(request, 'products/product_list.html', {
        'img': products,
        'wishlist_ids': wishlist_ids,
        'sort_by': sort_by,
    })


# ──────────────────────────────────────────────────────────
#  CART  (session-based)
# ──────────────────────────────────────────────────────────

@login_required
def cart(request):
    cart_data = request.session.get('cart', {})

    if request.method == 'POST':
        action = request.POST.get('action', 'add')
        product_id = request.POST.get('product_id')
        model_type = request.POST.get('model_type', 'product')
        key = request.POST.get('cart_key') or (f"{model_type}_{product_id}" if model_type else str(product_id))

        if action == 'remove':
            if key in cart_data:
                cart_data.pop(key, None)
            else:
                # Fallback: match by product_id & model_type or product_id
                keys_to_remove = [
                    k for k, v in cart_data.items()
                    if str(v.get('id')) == str(product_id) and v.get('model_type', 'product') == model_type
                ]
                if not keys_to_remove:
                    keys_to_remove = [k for k, v in cart_data.items() if str(v.get('id')) == str(product_id)]
                for k in keys_to_remove:
                    cart_data.pop(k, None)

            request.session['cart'] = cart_data
            messages.success(request, 'Item removed from your bag.')
            return redirect('cart')

        if action == 'update':
            qty = max(1, int(request.POST.get('update_quantity', 1) or 1))
            if key in cart_data:
                cart_data[key]['quantity'] = qty
            else:
                # Fallback: match by product_id & model_type or product_id
                updated_flag = False
                for k, v in cart_data.items():
                    if str(v.get('id')) == str(product_id) and v.get('model_type', 'product') == model_type:
                        cart_data[k]['quantity'] = qty
                        updated_flag = True
                        break
                if not updated_flag:
                    for k, v in cart_data.items():
                        if str(v.get('id')) == str(product_id):
                            cart_data[k]['quantity'] = qty
                            break

            request.session['cart'] = cart_data
            messages.success(request, 'Quantity updated in your bag.')
            return redirect('cart')

        # Default: add
        product = get_product_by_pk(product_id, model_type=model_type)
        if not product:
            product = get_object_or_404(Product, pk=product_id)

        quantity = max(1, int(request.POST.get('quantity', 1) or 1))
        current = cart_data.get(key, {}).get('quantity', 0)
        p_model = getattr(product, 'model_name', model_type or 'product')
        cart_data[key] = {
            'id': product.pk,
            'model_type': p_model,
            'name': product.name,
            'price': float(product.price),
            'discount': float(product.discount),
            'quantity': current + quantity,
            'image': product.image_url,
        }
        request.session['cart'] = cart_data
        messages.success(request, f'"{product.name}" added to your bag.')
        return redirect('cart')

    # GET — build cart items list
    cart_items = []
    total_discount = 0
    for key, item in cart_data.items():
        p_model = item.get('model_type', 'product')
        product = get_product_by_pk(item['id'], model_type=p_model)
        if product:
            original_price = item['price']
            discount_percent = item.get('discount', 0)
            discounted_price = original_price * (1 - discount_percent / 100) if discount_percent > 0 else original_price
            discounted_price = round(discounted_price, 2)
            item_total = round(discounted_price * item['quantity'], 2)
            item_discount_amount = round((original_price - discounted_price) * item['quantity'], 2)

            cart_items.append({
                'pk': item['id'],
                'cart_key': key,
                'product': product,
                'quantity': item['quantity'],
                'unit_price': original_price,
                'discount_percent': discount_percent,
                'discounted_price': discounted_price,
                'total': item_total,
                'discount_amount': item_discount_amount,
            })
            total_discount += item_discount_amount

    subtotal = round(sum(i['unit_price'] * i['quantity'] for i in cart_items), 2)
    discount_total = round(total_discount, 2)
    subtotal_after_discount = round(subtotal - discount_total, 2)
    shipping = 0 if subtotal_after_discount >= 999 else 99
    total = round(subtotal_after_discount + shipping, 2)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount_total': discount_total,
        'subtotal_after_discount': subtotal_after_discount,
        'shipping': shipping,
        'total': total,
    })


# ──────────────────────────────────────────────────────────
#  CHECKOUT — now saves Order + OrderItems to database
# ──────────────────────────────────────────────────────────

@login_required
def checkout(request):
    cart_data = request.session.get('cart', {})
    model_map = {'product': Product, 'men': Men, 'women': Women}

    # Build cart items from session
    cart_items = []
    total_discount = 0
    for key, item in cart_data.items():
        m_type = item.get('model_type', 'product')
        ModelClass = model_map.get(m_type, Product)
        try:
            product = ModelClass.objects.get(pk=item['id'])
            original_price = item['price']
            discount_percent = item.get('discount', 0)
            discounted_price = original_price * (1 - discount_percent / 100) if discount_percent > 0 else original_price
            discounted_price = round(discounted_price, 2)
            item_total = round(discounted_price * item['quantity'], 2)
            item_discount_amount = round((original_price - discounted_price) * item['quantity'], 2)

            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'unit_price': original_price,
                'discount_percent': discount_percent,
                'discounted_price': discounted_price,
                'total': item_total,
                'discount_amount': item_discount_amount,
            })
            total_discount += item_discount_amount
        except ModelClass.DoesNotExist:
            pass

    subtotal = round(sum(i['unit_price'] * i['quantity'] for i in cart_items), 2)
    discount_total = round(total_discount, 2)
    subtotal_after_discount = round(subtotal - discount_total, 2)
    shipping = 0 if subtotal_after_discount >= 999 else 99
    total = round(subtotal_after_discount + shipping, 2)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            if not cart_items:
                messages.error(request, 'Your cart is empty. Add items before checkout.')
                return redirect('cart')

            d = form.cleaned_data
            # ── Create the Order ─────────────────────────
            order_obj = Order.objects.create(
                user           = request.user,
                name           = d['firstname'],
                email          = d['email'],
                phone          = d['phone'],
                address        = d['address'],
                city           = d['city'],
                state          = d['state'],
                country        = d['country'],
                pincode        = d['pincode'],
                payment_method = d['method'],
                subtotal       = subtotal,
                discount       = discount_total,
                shipping_cost  = shipping,
                total_price    = total,
            )
            # ── Create OrderItems ─────────────────────────
            for item in cart_items:
                OrderItem.objects.create(
                    order        = order_obj,
                    product_name = item['product'].name,
                    brand_name   = 'STYLEVERSE',
                    quantity     = item['quantity'],
                    unit_price   = item['discounted_price'],
                )
            # ── Clear cart session ────────────────────────
            request.session['cart'] = {}
            messages.success(request, f'🎉 Order #{order_obj.order_number} placed successfully!')
            return redirect('orders')
        else:
            for field, errs in form.errors.items():
                for e in errs:
                    messages.error(request, f'{field}: {e}')
    else:
        form = CheckoutForm(initial={
            'email': request.user.email,
            'firstname': request.user.first_name or request.user.username,
            'country': 'India',
        })

    return render(request, 'checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount_total': discount_total,
        'subtotal_after_discount': subtotal_after_discount,
        'shipping': shipping,
        'total': total,
        'grand_total': total,
    })


# ──────────────────────────────────────────────────────────
#  MY ORDERS — now queries real DB orders
# ──────────────────────────────────────────────────────────

@login_required
def order(request):
    user_orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-order_date')
    return render(request, 'orders.html', {'orders': user_orders})


# ──────────────────────────────────────────────────────────
#  INVOICE — now accepts order_id and shows real data
# ──────────────────────────────────────────────────────────

@login_required
def invoice(request, order_id):
    order_obj = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'invoice.html', {'order': order_obj, 'is_admin': False})


# ──────────────────────────────────────────────────────────
#  WISHLIST
# ──────────────────────────────────────────────────────────

@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user).order_by('-added_at')
    return render(request, 'wishlist.html', {'wishlist_items': items})


@login_required
def toggle_wishlist(request):
    if request.method == 'POST':
        model_type = request.POST.get('model_type', 'product')
        object_id = request.POST.get('object_id')
        model_map = {'product': Product, 'men': Men, 'women': Women}
        ModelClass = model_map.get(model_type)
        if not ModelClass or not object_id:
            return redirect(request.META.get('HTTP_REFERER', 'product_list'))
        obj = get_object_or_404(ModelClass, pk=object_id)
        existing = Wishlist.objects.filter(user=request.user, model_type=model_type, object_id=object_id).first()
        if existing:
            existing.delete()
            messages.info(request, f'Removed "{obj.name}" from your wishlist.')
        else:
            Wishlist.objects.create(
                user=request.user,
                model_type=model_type,
                object_id=obj.pk,
                name=obj.name,
                price=obj.price,
                image_url=obj.image_url,
            )
            messages.success(request, f'Added "{obj.name}" to your wishlist.')
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


# ──────────────────────────────────────────────────────────
#  CATEGORY PAGES
# ──────────────────────────────────────────────────────────

def men(request):
    sort_by = request.GET.get('sort', '-pk')
    allowed = ['-pk', 'pk', 'price', '-price']
    if sort_by not in allowed:
        sort_by = '-pk'
    products = Men.objects.all().order_by(sort_by)
    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(
            Wishlist.objects.filter(user=request.user, model_type='men').values_list('object_id', flat=True)
        )
    return render(request, 'mens/men.html', {
        'img': products,
        'wishlist_ids': wishlist_ids,
        'sort_by': sort_by,
    })


def women(request):
    sort_by = request.GET.get('sort', '-pk')
    allowed = ['-pk', 'pk', 'price', '-price']
    if sort_by not in allowed:
        sort_by = '-pk'
    products = Women.objects.all().order_by(sort_by)
    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(
            Wishlist.objects.filter(user=request.user, model_type='women').values_list('object_id', flat=True)
        )
    return render(request, 'womens/women.html', {
        'img': products,
        'wishlist_ids': wishlist_ids,
        'sort_by': sort_by,
    })


# ──────────────────────────────────────────────────────────
#  AUTH
# ──────────────────────────────────────────────────────────

def register(request):
    initial_type = request.GET.get('type', 'customer')
    if initial_type not in ['customer', 'sub_admin']:
        initial_type = 'customer'

    if request.method == 'POST':
        action_type = request.POST.get('account_type', 'customer')
        if action_type == 'sub_admin':
            seller_form = SubAdminRequestForm(request.POST)
            user_form = RegisterUserForm(initial={'account_type': 'customer'})
            if seller_form.is_valid():
                req_obj = seller_form.save()

                import random, string
                pwd_display = req_obj.requested_password if req_obj.requested_password else ('SV-Seller#' + ''.join(random.choices(string.digits, k=6)))
                if not req_obj.requested_password:
                    req_obj.requested_password = pwd_display
                    req_obj.save()

                seller_login_url = request.build_absolute_uri('/seller/login/')

                # ── 1. Notify super admin about new seller registration (with password details) ──────
                try:
                    superusers = User.objects.filter(is_superuser=True, is_active=True)
                    admin_emails = [u.email for u in superusers if u.email]
                    if not admin_emails:
                        admin_emails = [settings.EMAIL_HOST_USER]  # fallback to host only

                    subj = f"[STYLEVERSE] New Seller Sub-Admin Registered: {req_obj.store_name}"
                    admin_msg = f"""Hello Super Admin,

A new Sub-Admin / Seller has registered on STYLEVERSE for store '{req_obj.store_name}'.

Sub-Admin Registration Details:
------------------------------------------
Full Name       : {req_obj.full_name}
Username        : {req_obj.username}
Seller Email    : {req_obj.email}
Phone           : {req_obj.phone}
Store Name      : {req_obj.store_name}
Login Password  : {pwd_display}
Business Reason : {req_obj.reason}

Seller Portal Link:
{seller_login_url}

Super Admin Panel Review / Approval Link:
{request.build_absolute_uri('/admin/shopapp/subadminrequest/')}

Thank you,
STYLEVERSE System Notification
"""
                    send_mail(subj, admin_msg, settings.EMAIL_HOST_USER, admin_emails, fail_silently=True)
                except Exception as e:
                    print("Error sending seller request mail to admin:", e)

                # ── 2. Send confirmation with login password to Seller's Email ID ───────
                try:
                    applicant_subject = f"🎉 [STYLEVERSE] Sub-Admin / Seller Account Details — {req_obj.store_name}"
                    applicant_msg = f"""Hello {req_obj.full_name},

Thank you for registering as a STYLEVERSE Seller!

Your Sub-Admin Seller account has been created for store '{req_obj.store_name}'.

Your Login Credentials:
------------------------------------------
Store Name  : {req_obj.store_name}
Username    : {req_obj.username}
Email ID    : {req_obj.email}
Password    : {pwd_display}

Exclusive Seller Portal Login Link:
{seller_login_url}

Important Instructions:
1. Access the Seller Panel using the link above: {seller_login_url}
2. Use your Username ({req_obj.username}) and Password to log in.
3. If your account requires Super-Admin approval, your status is recorded and credentials will activate upon approval.

Thank you,
STYLEVERSE Team
"""
                    send_mail(applicant_subject, applicant_msg, settings.EMAIL_HOST_USER, [req_obj.email], fail_silently=True)
                except Exception as e:
                    print("Error sending confirmation email to applicant:", e)

                messages.success(request, f'🎉 Seller application for "{req_obj.store_name}" registered successfully! Password and account details have been sent to your email ({req_obj.email}) and Super Admin.')
                return redirect('register')
        else:
            user_form = RegisterUserForm(request.POST)
            seller_form = SubAdminRequestForm()
            if user_form.is_valid():
                user = user_form.save()

                # ── Send welcome email to the newly registered customer ─────
                try:
                    if user.email:
                        welcome_subject = "🎉 Welcome to STYLEVERSE — Your Account is Ready!"
                        welcome_msg = f"""Hello {user.first_name or user.username},

Welcome to STYLEVERSE — your premium fashion destination!

Your account has been created successfully.

Account Details:
------------------------------------------
Username : {user.username}
Email    : {user.email}

You can now:
✔ Browse our exclusive collections
✔ Save items to your wishlist
✔ Track your orders
✔ Enjoy member-only deals

Log in now and start shopping: http://127.0.0.1:1111/login/

Thank you for joining STYLEVERSE!

— The STYLEVERSE Team
"""
                        send_mail(welcome_subject, welcome_msg, settings.EMAIL_HOST_USER, [user.email], fail_silently=True)
                except Exception as e:
                    print("Error sending welcome email to user:", e)

                messages.success(request, f'🎉 Account for "{user.username}" created! A welcome email has been sent to {user.email}. Please sign in.')
                return redirect('login')
    else:
        user_form = RegisterUserForm(initial={'account_type': initial_type})
        seller_form = SubAdminRequestForm()

    selected_type = request.POST.get('account_type', initial_type) if request.method == 'POST' else initial_type
    return render(request, 'login/register.html', {
        'form': user_form,
        'seller_form': seller_form,
        'account_type': selected_type
    })


def login(request):
    # Already logged in — redirect based on role
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_index')
        return redirect('index')

    if request.method == 'POST':
        form = LoginUserForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                is_new_user = (user.last_login is None)
                auth_login(request, user)

                display_name = user.first_name or user.username
                if is_new_user:
                    messages.success(request, f'🎉 Welcome to STYLEVERSE, {display_name}! We are thrilled to have you join us.')
                else:
                    messages.success(request, f'✨ Welcome back to STYLEVERSE, {display_name}!')

                # ── Role-based redirect after login ───────────────
                if user.is_staff or user.is_superuser:
                    return redirect('admin_index')
                else:
                    return redirect('index')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginUserForm()
    return render(request, 'login/login.html', {'form': form})


def forgotpassword(request):
    """Forgot password page — allows unauthenticated users to reset their password by username."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        new_password1 = request.POST.get('new_password1', '')
        new_password2 = request.POST.get('new_password2', '')

        if not username:
            messages.error(request, 'Please enter your username.')
        elif not new_password1 or not new_password2:
            messages.error(request, 'Please fill in both password fields.')
        elif new_password1 != new_password2:
            messages.error(request, 'Passwords do not match. Please try again.')
        elif len(new_password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        else:
            try:
                user = User.objects.get(username=username)
                user.set_password(new_password1)
                user.save()

                # ── Send password-reset confirmation to the user's own email ──
                if user.email:
                    try:
                        reset_subject = "[STYLEVERSE] Your Password Has Been Reset"
                        reset_msg = f"""Hello {user.first_name or user.username},

Your STYLEVERSE account password has been successfully reset.

Account Details:
------------------------------------------
Username : {user.username}
Email    : {user.email}

If you did NOT request this change, please contact us immediately.

You can now log in with your new password:
http://127.0.0.1:1111/login/

Thank you,
STYLEVERSE Security Team
"""
                        send_mail(reset_subject, reset_msg, settings.EMAIL_HOST_USER, [user.email], fail_silently=True)
                    except Exception as e:
                        print("Error sending password reset email:", e)

                messages.success(request, f'Password reset successfully! A confirmation has been sent to your registered email. Please sign in.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'No account found with that username.')

    return render(request, 'login/forgotpassword.html')




@login_required
def profile_user(request):
    return render(request, 'login/profile.html')


# ──────────────────────────────────────────────────────────
#  EDIT PROFILE — now saves UserProfile to database
# ──────────────────────────────────────────────────────────

@login_required
def editprofile(request):
    # Get or create UserProfile for this user
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'fname': request.user.first_name,
            'lname': request.user.last_name,
            'email': request.user.email,
            'bio': '', 'contact': '', 'gender': '', 'address': '',
        }
    )
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            # also sync email back to auth User
            request.user.email = form.cleaned_data['email']
            request.user.first_name = form.cleaned_data['fname']
            request.user.last_name = form.cleaned_data['lname']
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('editprofile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'login/editprofile.html', {'form': form, 'profile': profile})


@login_required
def changepassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated successfully!')
            return redirect('editprofile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'login/changepassword.html', {'form': form})


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')


@login_required
def card(request):
    return render(request, 'products/product_card.html')



