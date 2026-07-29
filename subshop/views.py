from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash
from shopapp.forms import LoginUserForm
from shopapp.models import (
    Product, Men, Women, ProductRequest, Order, Contact, 
    AdminDiscussion, AdminDiscussionReply, UserProfile
)
from shopapp.decorators import admin_required


def get_all_combined_products(sort_by='-pk'):
    """Combines products from Product, Men, and Women models dynamically."""
    p1 = list(Product.objects.all())
    p2 = list(Men.objects.all())
    p3 = list(Women.objects.all())
    all_prods = p1 + p2 + p3
    reverse = sort_by.startswith('-')
    all_prods.sort(key=lambda x: x.pk, reverse=reverse)
    return all_prods


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


def admin_login(request):
    """Exclusive Seller & Sub-Admin Login Portal."""
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_index')
        else:
            messages.error(request, 'Access denied. You are logged in as a customer. Please log in with a Sub-Admin account.')
            return redirect('index')

    if request.method == 'POST':
        form = LoginUserForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_staff or user.is_superuser:
                    auth_login(request, user)
                    messages.success(request, f'⚡ Welcome, Seller {user.username}! You are now logged in to the Admin Panel.')
                    return redirect('admin_index')
                else:
                    messages.error(request, '⛔ Access Denied. Your account is a Customer account. Please use the customer login page or apply for Seller access.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginUserForm()

    return render(request, 'sub-admin/admin_login.html', {'form': form})


@admin_required
def admin_index(request):
    """Admin dashboard with stats."""
    total_users    = User.objects.count()
    total_products = Product.objects.count() + Men.objects.count() + Women.objects.count()
    total_orders   = Order.objects.count()
    total_messages = Contact.objects.count()
    pending_total  = Order.objects.filter(payment_status='pending').aggregate(s=Sum('total_price'))['s'] or 0
    completed_total = Order.objects.filter(payment_status='completed').aggregate(s=Sum('total_price'))['s'] or 0
    recent_orders  = Order.objects.order_by('-order_date')[:5]

    if request.user.is_superuser:
        pending_requests = ProductRequest.objects.filter(status='pending').order_by('-created_at')[:5]
    else:
        pending_requests = ProductRequest.objects.filter(user=request.user, status='pending').order_by('-created_at')[:5]

    return render(request, 'sub-admin/dashboard.html', {
        'total_users':      total_users,
        'total_products':   total_products,
        'total_orders':     total_orders,
        'total_messages':   total_messages,
        'pending_total':    pending_total,
        'completed_total':  completed_total,
        'recent_orders':    recent_orders,
        'pending_requests': pending_requests,
    })


@admin_required
def admin_orders(request):
    """Admin: list all orders, update payment status, delete."""
    if request.method == 'POST' and 'update_order' in request.POST:
        order_obj = get_object_or_404(Order, pk=request.POST.get('order_id'))
        order_obj.payment_status = request.POST.get('update_payment', 'pending')
        order_obj.status         = request.POST.get('update_status', 'processing')
        order_obj.updated_date   = timezone.now()
        order_obj.save()
        messages.success(request, f'Order #{order_obj.order_number} updated.')
        return redirect('admin_orders')

    if 'delete' in request.GET:
        if not request.user.is_superuser:
            messages.error(request, '⛔ Only Super Admins can delete orders.')
            return redirect('admin_orders')
        order_obj = get_object_or_404(Order, pk=request.GET['delete'])
        order_obj.delete()
        messages.success(request, 'Order deleted.')
        return redirect('admin_orders')

    all_orders = Order.objects.all().prefetch_related('items').order_by('-order_date')
    return render(request, 'sub-admin/orders.html', {'orders': all_orders})


@admin_required
def admin_products(request):
    """Admin: list all products, manage product requests & approvals."""
    model_map = {'product': Product, 'men': Men, 'women': Women}

    if request.method == 'POST':
        action = request.POST.get('action')

        # ── SUB ADMIN: Submit Add Product Request
        if action == 'request_add':
            category = request.POST.get('category', 'product')
            name = request.POST.get('name', '').strip()
            raw_price = request.POST.get('price', '').strip()
            raw_discount = request.POST.get('discount', '').strip()

            try:
                price = float(raw_price) if raw_price else 0.0
            except ValueError:
                price = 0.0

            try:
                discount = float(raw_discount) if raw_discount else 0.0
            except ValueError:
                discount = 0.0

            image = request.FILES.get('image')

            # Create product request pending Super Admin approval
            req = ProductRequest.objects.create(
                user=request.user,
                request_type='add',
                category=category,
                name=name,
                price=price,
                discount=discount,
                image=image,
                status='pending'
            )
            notify_super_admin_product_request(req, request)
            return redirect(f"{request.path}?tab=requests")

        # ── SUB ADMIN: Direct Edit Product (Instant Update)
        elif action in ['direct_edit', 'request_edit']:
            target_id = request.POST.get('target_id')
            category = request.POST.get('category', 'product')
            name = request.POST.get('name', '').strip()
            raw_price = request.POST.get('price', '').strip()
            raw_discount = request.POST.get('discount', '').strip()

            try:
                price = float(raw_price) if raw_price else 0.0
            except ValueError:
                price = 0.0

            try:
                discount = float(raw_discount) if raw_discount else 0.0
            except ValueError:
                discount = 0.0

            image = request.FILES.get('image')

            ModelClass = model_map.get(category, Product)
            target_obj = get_object_or_404(ModelClass, pk=target_id)

            target_obj.name = name
            target_obj.price = price
            target_obj.discount = discount
            if image:
                target_obj.image = image
            if not target_obj.created_by:
                target_obj.created_by = request.user
            target_obj.save()

            messages.success(request, f'🎉 Product "{target_obj.name}" updated successfully!')
            return redirect('admin_products')

    # Cancel / Remove Product Request
    if 'cancel_request' in request.GET:
        req_id = request.GET['cancel_request']
        if request.user.is_superuser:
            req_obj = get_object_or_404(ProductRequest, pk=req_id)
        else:
            req_obj = get_object_or_404(ProductRequest, pk=req_id, user=request.user)

        req_name = req_obj.name
        req_obj.delete()
        messages.success(request, f'Product request for "{req_name}" has been cancelled.')
        return redirect(f"{request.path}?tab=requests")

    # Delete product
    if 'delete_product' in request.GET:
        if not request.user.is_superuser:
            messages.error(request, '⛔ Only Super Admins can delete products directly.')
            return redirect('admin_products')
        pk = request.GET['delete_product']
        model = request.GET.get('model', 'product')
        M = model_map.get(model, Product)
        obj = get_object_or_404(M, pk=pk)
        obj.delete()
        messages.success(request, 'Product deleted.')
        return redirect('admin_products')

    all_products = get_all_combined_products('-pk')
    men_products = Men.objects.all().order_by('-pk')
    women_products = Women.objects.all().order_by('-pk')

    if request.user.is_superuser:
        pending_requests = ProductRequest.objects.filter(status='pending').order_by('-created_at')
        my_requests = ProductRequest.objects.all().order_by('-created_at')[:15]
    else:
        pending_requests = ProductRequest.objects.filter(user=request.user, status='pending').order_by('-created_at')
        my_requests = ProductRequest.objects.filter(user=request.user).order_by('-created_at')[:15]

    return render(request, 'sub-admin/products.html', {
        'all_products':     all_products,
        'men_products':     men_products,
        'women_products':   women_products,
        'pending_requests': pending_requests,
        'my_requests':      my_requests,
    })


@admin_required
def admin_people(request):
    """Admin: list all users (Super Admin only)."""
    if not request.user.is_superuser:
        return redirect('admin_index')
    all_users = User.objects.all().order_by('-date_joined')
    return render(request, 'sub-admin/people.html', {'users': all_users})


@admin_required
def admin_messages_view(request):
    """Admin: view/review contact messages."""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'save_review':
            msg_id = request.POST.get('msg_id')
            msg_obj = get_object_or_404(Contact, pk=msg_id)
            msg_obj.status = request.POST.get('status', 'new')
            msg_obj.admin_review = request.POST.get('admin_review', '').strip()
            msg_obj.reviewed_by = request.user
            msg_obj.save()
            messages.success(request, f'Review & status saved for message from {msg_obj.Name}.')
            return redirect('admin_messages')

    if 'delete_msg' in request.GET:
        msg = get_object_or_404(Contact, pk=request.GET['delete_msg'])
        msg.delete()
        messages.success(request, 'Message deleted.')
        return redirect('admin_messages')

    contact_messages = Contact.objects.all().order_by('-pk')
    return render(request, 'sub-admin/messages.html', {
        'contact_messages': contact_messages,
        'messages_count': contact_messages.count(),
    })


@admin_required
def admin_discussions_view(request):
    """Private discussion board connecting Super-Admin & Sub-Admins."""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Post new discussion topic
        if action == 'create_topic':
            title = request.POST.get('title', '').strip()
            message = request.POST.get('message', '').strip()
            is_important = request.POST.get('is_important') == 'true'
            recipient_raw = request.POST.get('recipient', 'group')

            recipient_user = None
            disc_type = 'group'

            if request.user.is_superuser:
                if recipient_raw != 'group' and recipient_raw.isdigit():
                    recipient_user = User.objects.filter(pk=int(recipient_raw)).first()
                    if recipient_user:
                        disc_type = 'individual'
            else:
                # Sub-Admin: Default recipient is Super-Admin
                super_admin = User.objects.filter(is_superuser=True, is_active=True).first()
                recipient_user = super_admin
                disc_type = 'individual' if super_admin else 'group'

            if title and message:
                AdminDiscussion.objects.create(
                    sender=request.user,
                    recipient=recipient_user,
                    discussion_type=disc_type,
                    title=title,
                    message=message,
                    is_important=is_important
                )
                recip_name = recipient_user.username if recipient_user else "All Sub-Admins"
                messages.success(request, f'Discussion topic "{title}" sent to {recip_name}!')
            return redirect('admin_discussions')

        # Reply to existing discussion
        elif action == 'post_reply':
            topic_id = request.POST.get('topic_id')
            reply_text = request.POST.get('reply_text', '').strip()
            topic = get_object_or_404(AdminDiscussion, pk=topic_id)
            if reply_text:
                AdminDiscussionReply.objects.create(
                    discussion=topic,
                    sender=request.user,
                    reply_text=reply_text
                )
                messages.success(request, 'Reply posted successfully.')
            return redirect('admin_discussions')

    # Query discussions based on user role
    if request.user.is_superuser:
        discussions = AdminDiscussion.objects.all().prefetch_related('replies', 'replies__sender', 'sender', 'recipient')
    else:
        discussions = AdminDiscussion.objects.filter(
            Q(discussion_type='group') | Q(sender=request.user) | Q(recipient=request.user)
        ).distinct().prefetch_related('replies', 'replies__sender', 'sender', 'recipient')

    sub_admins = User.objects.filter(is_staff=True, is_superuser=False, is_active=True)
    super_admin = User.objects.filter(is_superuser=True, is_active=True).first()

    return render(request, 'sub-admin/discussions.html', {
        'discussions': discussions,
        'sub_admins': sub_admins,
        'super_admin': super_admin,
    })


@admin_required
def admin_invoice(request, order_id):
    """Admin: view invoice for any order."""
    order_obj = get_object_or_404(Order, pk=order_id)
    return render(request, 'invoice.html', {'order': order_obj, 'is_admin': True})


@admin_required
def admin_delivery(request):
    """Seller Panel: Delivery & Logistics Management Section."""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_delivery':
            order_id = request.POST.get('order_id')
            order_obj = get_object_or_404(Order, pk=order_id)
            
            new_status = request.POST.get('status')
            courier = request.POST.get('courier_partner', '').strip()
            tracking = request.POST.get('tracking_number', '').strip()
            est_date = request.POST.get('estimated_delivery')
            notes = request.POST.get('delivery_notes', '').strip()

            if new_status in dict(Order.ORDER_STATUS_CHOICES):
                order_obj.status = new_status
            if courier:
                order_obj.courier_partner = courier
            if tracking:
                order_obj.tracking_number = tracking
            if est_date:
                try:
                    order_obj.estimated_delivery = est_date
                except Exception:
                    pass
            if notes:
                order_obj.delivery_notes = notes

            order_obj.save()
            messages.success(request, f'🚚 Delivery status for Order #{order_obj.order_number} updated to "{order_obj.get_status_display()}"!')
            return redirect('admin_delivery')

    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '').strip()

    orders = Order.objects.all()
    if status_filter != 'all':
        orders = orders.filter(status=status_filter)
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(tracking_number__icontains=search_query)
        )

    # Delivery KPI statistics
    total_orders = Order.objects.count()
    processing_count = Order.objects.filter(status='processing').count()
    shipped_count = Order.objects.filter(status='shipped').count()
    delivered_count = Order.objects.filter(status='delivered').count()
    cancelled_count = Order.objects.filter(status='cancelled').count()

    return render(request, 'sub-admin/delivery.html', {
        'orders': orders,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_orders': total_orders,
        'processing_count': processing_count,
        'shipped_count': shipped_count,
        'delivered_count': delivered_count,
        'cancelled_count': cancelled_count,
    })


@admin_required
def admin_stock(request):
    """Seller Panel: Individual Stock & Inventory Details Section."""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_stock':
            cat = request.POST.get('category')
            prod_id = request.POST.get('product_id')
            new_stock = request.POST.get('stock')

            try:
                stock_val = max(0, int(new_stock))
                if cat == 'men':
                    prod_item = get_object_or_404(Men, pk=prod_id)
                elif cat == 'women':
                    prod_item = get_object_or_404(Women, pk=prod_id)
                else:
                    prod_item = get_object_or_404(Product, pk=prod_id)

                prod_item.stock = stock_val
                prod_item.save()
                messages.success(request, f'📦 Stock for "{prod_item.name}" updated to {stock_val} units!')
            except (ValueError, TypeError):
                messages.error(request, 'Invalid stock quantity entered.')
            return redirect('admin_stock')

    # Get combined product list with category tag and stock status
    p1 = list(Product.objects.all())
    for p in p1: p.category_label = 'General'
    p2 = list(Men.objects.all())
    for p in p2: p.category_label = 'Men'
    p3 = list(Women.objects.all())
    for p in p3: p.category_label = 'Women'

    all_products = p1 + p2 + p3
    all_products.sort(key=lambda x: x.stock)

    stock_filter = request.GET.get('filter', 'all')
    search_q = request.GET.get('q', '').strip().lower()

    if search_q:
        all_products = [p for p in all_products if search_q in p.name.lower() or search_q in p.category_label.lower()]

    if stock_filter == 'low':
        all_products = [p for p in all_products if p.is_low_stock()]
    elif stock_filter == 'out':
        all_products = [p for p in all_products if p.is_out_of_stock()]
    elif stock_filter == 'in_stock':
        all_products = [p for p in all_products if p.stock > 5]

    # Inventory summary KPI stats
    all_raw = list(Product.objects.all()) + list(Men.objects.all()) + list(Women.objects.all())
    total_items = len(all_raw)
    in_stock_count = sum(1 for p in all_raw if p.stock > 5)
    low_stock_count = sum(1 for p in all_raw if p.is_low_stock())
    out_stock_count = sum(1 for p in all_raw if p.is_out_of_stock())

    return render(request, 'sub-admin/stock.html', {
        'products': all_products,
        'stock_filter': stock_filter,
        'search_q': request.GET.get('q', ''),
        'total_items': total_items,
        'in_stock_count': in_stock_count,
        'low_stock_count': low_stock_count,
        'out_stock_count': out_stock_count,
    })


def notify_super_admin_profile_update(user, update_type):
    """Notify super admins whenever a sub-admin updates their password or profile info."""
    try:
        superusers = User.objects.filter(is_superuser=True, is_active=True)
        emails = [u.email for u in superusers if u.email]
        if not emails:
            emails = [settings.EMAIL_HOST_USER]

        if update_type == 'password':
            subject = f"[STYLEVERSE Security Alert] Sub-Admin Password Changed: {user.username}"
            message = f"""Hello Super Admin,

Notice: Sub-Admin account '{user.username}' has successfully updated their password.

Security Event Details:
----------------------------------
Sub-Admin Username : {user.username}
Sub-Admin Email    : {user.email or 'N/A'}
Action Performed   : Password Change
Timestamp          : {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

If you did not authorize this change, please review user access immediately in Jazzmin Super Admin:
http://127.0.0.1:1111/admin/auth/user/

Thank you,
STYLEVERSE Security System
"""
        else:
            subject = f"[STYLEVERSE Notice] Sub-Admin Profile Updated: {user.username}"
            message = f"""Hello Super Admin,

Notice: Sub-Admin user '{user.username}' has updated their profile details.

Updated Account Summary:
----------------------------------
Username  : {user.username}
Full Name : {user.get_full_name() or user.username}
Email     : {user.email or 'N/A'}
Action    : Profile Information Updated
Timestamp : {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

You can view and manage sub-admins in the Super Admin panel:
http://127.0.0.1:1111/admin/auth/user/

Thank you,
STYLEVERSE Admin Notification System
"""

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=emails,
            fail_silently=True
        )
    except Exception:
        pass


@admin_required
def admin_profile(request):
    """View and update sub-admin / seller profile and security details."""
    initial_fname = request.user.first_name
    if not initial_fname and not ('@' in request.user.username):
        initial_fname = request.user.username

    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'fname': initial_fname or '',
            'lname': request.user.last_name or '',
            'email': request.user.email or '',
            'contact': '',
            'gender': 'Not Specified',
            'address': '',
            'bio': 'Sub Admin / Seller at STYLEVERSE Store'
        }
    )

    # Clean profile.fname if it currently holds a username containing '@'
    if profile.fname == request.user.username and '@' in profile.fname:
        profile.fname = request.user.first_name or ''
        profile.save()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            username = request.POST.get('username', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            contact = request.POST.get('contact', '').strip()
            gender = request.POST.get('gender', '').strip()
            birthdate = request.POST.get('birthdate', '').strip()
            bio = request.POST.get('bio', '').strip()
            address = request.POST.get('address', '').strip()

            # Validate unique username
            if username and username != request.user.username:
                if User.objects.filter(username=username).exclude(pk=request.user.pk).exists():
                    messages.error(request, f'Username "{username}" is already taken by another account.')
                    return redirect('admin_profile')

            # Update User model
            user = request.user
            if username:
                user.username = username
            user.first_name = first_name
            user.last_name = last_name
            if email:
                user.email = email
            user.save()

            # Update UserProfile model
            profile.fname = first_name
            profile.lname = last_name
            profile.email = email
            profile.contact = contact
            profile.gender = gender or 'Not Specified'
            profile.bio = bio
            profile.address = address

            if birthdate:
                try:
                    profile.birthdate = birthdate
                except Exception:
                    pass

            profile.save()
            notify_super_admin_profile_update(request.user, update_type='profile')
            messages.success(request, '👤 Profile details updated successfully! Super-Admin notified via email.')
            return redirect('admin_profile')

        elif action == 'change_password':
            current_pass = request.POST.get('current_password', '')
            new_pass = request.POST.get('new_password', '')
            confirm_pass = request.POST.get('confirm_password', '')

            if not request.user.check_password(current_pass):
                messages.error(request, 'Incorrect current password. Please try again.')
            elif len(new_pass) < 6:
                messages.error(request, 'New password must be at least 6 characters long.')
            elif new_pass != confirm_pass:
                messages.error(request, 'New passwords do not match. Please re-enter.')
            else:
                request.user.set_password(new_pass)
                request.user.save()
                update_session_auth_hash(request, request.user)
                notify_super_admin_profile_update(request.user, update_type='password')
                messages.success(request, '🔐 Password changed successfully! Super-Admin notified via email.')
            return redirect('admin_profile')

    return render(request, 'sub-admin/profile.html', {
        'profile': profile,
    })