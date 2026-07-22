from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth import authenticate, login as auth_login
from shopapp.forms import LoginUserForm
from shopapp.models import (
    Product, Men, Women, ProductRequest, Order, Contact, 
    AdminDiscussion, AdminDiscussionReply
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

        # ── SUB ADMIN: Submit Edit Product Request
        elif action == 'request_edit':
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

            req = ProductRequest.objects.create(
                user=request.user,
                request_type='edit',
                category=category,
                target_id=target_id,
                name=name,
                price=price,
                discount=discount,
                image=image if image else (target_obj.image.name if target_obj.image else None),
                status='pending'
            )
            notify_super_admin_product_request(req, request)
            return redirect(f"{request.path}?tab=requests")

    # Delete product
    if 'delete_product' in request.GET:
        if not request.user.is_superuser:
            messages.error(request, '⛔ Only Super Admins can delete products directly. Please submit an edit request instead.')
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
    """Admin: list all users."""
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