from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import path
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from shopapp.models import *
from django.contrib.auth.models import User
from shopapp.admin_custome import CustomerAdminSite


admin.site.site_header = 'STYLEVERSE Super Admin'
admin.site.site_title = 'STYLEVERSE Super Admin'
admin.site.index_title = 'Super Admin Dashboard'

customer_admin_site = CustomerAdminSite(name='customer_admin')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('Name', 'Surname', 'Email', 'status_badge', 'reviewed_by_user', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('Name', 'Surname', 'Email', 'Message', 'admin_review')
    readonly_fields = ('Name', 'Surname', 'Email', 'Message', 'created_at')
    fields = ('Name', 'Surname', 'Email', 'Message', 'status', 'admin_review', 'reviewed_by', 'created_at')
    list_per_page = 20

    def status_badge(self, obj):
        colors = {'new': '#3498db', 'in_progress': '#f1c40f', 'resolved': '#27ae60'}
        return format_html('<span style="background:{}; color:#fff; padding:3px 8px; border-radius:4px; font-size:11px; font-weight:bold; text-transform:uppercase;">{}</span>', colors.get(obj.status, '#7f8c8d'), obj.get_status_display())
    status_badge.short_description = 'Status'

    def reviewed_by_user(self, obj):
        return obj.reviewed_by.username if obj.reviewed_by else '-'
    reviewed_by_user.short_description = 'Reviewed By'


class AdminDiscussionReplyInline(admin.TabularInline):
    model = AdminDiscussionReply
    extra = 1
    readonly_fields = ('created_at',)


@admin.register(AdminDiscussion)
class AdminDiscussionAdmin(admin.ModelAdmin):
    list_display = ('title', 'sender', 'recipient_display', 'discussion_type', 'is_important', 'created_at')
    list_filter = ('discussion_type', 'is_important', 'created_at')
    search_fields = ('title', 'message', 'sender__username', 'recipient__username')
    inlines = [AdminDiscussionReplyInline]

    def recipient_display(self, obj):
        return obj.recipient.username if obj.recipient else 'Group (All Sub-Admins)'
    recipient_display.short_description = 'Recipient'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount', 'get_discounted_price', 'image')
    search_fields = ('name',)
    list_filter = ('price', 'discount')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'image')
        }),
        ('Pricing', {
            'fields': ('price', 'discount'),
            'description': 'Set the discount as a percentage (0-100)'
        }),
    )
    
    def get_discounted_price(self, obj):
        return f"₹{obj.get_discounted_price()}"
    get_discounted_price.short_description = 'Final Price'


@admin.register(Men)
class MenAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount', 'get_discounted_price', 'image')
    search_fields = ('name',)
    list_filter = ('price', 'discount')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'image')
        }),
        ('Pricing', {
            'fields': ('price', 'discount'),
            'description': 'Set the discount as a percentage (0-100)'
        }),
    )
    
    def get_discounted_price(self, obj):
        return f"₹{obj.get_discounted_price()}"
    get_discounted_price.short_description = 'Final Price'


@admin.register(Women)
class WomenAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount', 'get_discounted_price', 'image')
    search_fields = ('name',)
    list_filter = ('price', 'discount')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'image')
        }),
        ('Pricing', {
            'fields': ('price', 'discount'),
            'description': 'Set the discount as a percentage (0-100)'
        }),
    )
    
    def get_discounted_price(self, obj):
        return f"₹{obj.get_discounted_price()}"
    get_discounted_price.short_description = 'Final Price'



@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'email')
    search_fields = ('firstname', 'lastname', 'email')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'name', 'email', 'phone', 'payment_method', 'payment_status', 'status', 'total_price', 'order_date')
    list_filter  = ('payment_status', 'status', 'payment_method')
    search_fields = ('order_number', 'name', 'email', 'phone')
    readonly_fields = ('order_number', 'order_date')
    list_per_page = 20


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'quantity', 'unit_price', 'sub_total')
    search_fields = ('product_name',)


@admin.register(ProductRequest)
class ProductRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'request_type_badge', 'category', 'price_display', 'user', 'status_badge', 'approve_reject_buttons', 'created_at')
    list_filter = ('status', 'request_type', 'category')
    search_fields = ('name', 'user__username')
    list_per_page = 20
    actions = ['approve_requests', 'reject_requests']

    def request_type_badge(self, obj):
        color = '#3498db' if obj.request_type == 'add' else '#f1c40f'
        return format_html('<span style="background:{}; color:#fff; padding:3px 8px; border-radius:4px; font-weight:bold; font-size:11px; text-transform:uppercase;">{}</span>', color, obj.get_request_type_display())
    request_type_badge.short_description = 'Type'

    def status_badge(self, obj):
        colors = {'pending': '#e67e22', 'approved': '#27ae60', 'rejected': '#e74c3c'}
        color = colors.get(obj.status, '#7f8c8d')
        return format_html('<span style="background:{}; color:#fff; padding:3px 8px; border-radius:4px; font-weight:bold; font-size:11px; text-transform:uppercase;">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'

    def price_display(self, obj):
        if obj.discount > 0:
            return format_html('₹{} <small style="color:#e74c3c;">({}% off)</small>', obj.price, int(obj.discount))
        return f"₹{obj.price}"
    price_display.short_description = 'Price'

    def approve_reject_buttons(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a class="button" style="background:#27ae60; color:#fff; padding:4px 8px; border-radius:4px; font-weight:bold; text-decoration:none; margin-right:4px;" href="{}">Approve</a>'
                '<a class="button" style="background:#e74c3c; color:#fff; padding:4px 8px; border-radius:4px; font-weight:bold; text-decoration:none;" href="{}">Reject</a>',
                f'approve/{obj.pk}/',
                f'reject/{obj.pk}/'
            )
        return mark_safe('<span style="color:#888;">Processed</span>')
    approve_reject_buttons.short_description = 'Actions'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('approve/<int:req_id>/', self.admin_site.admin_view(self.approve_single_request), name='productrequest-approve'),
            path('reject/<int:req_id>/', self.admin_site.admin_view(self.reject_single_request), name='productrequest-reject'),
        ]
        return custom_urls + urls

    def approve_single_request(self, request, req_id):
        req_obj = get_object_or_404(ProductRequest, pk=req_id)
        self._process_approval(req_obj)
        messages.success(request, f'Approved & published product "{req_obj.name}".')
        return redirect('admin:shopapp_productrequest_changelist')

    def reject_single_request(self, request, req_id):
        req_obj = get_object_or_404(ProductRequest, pk=req_id)
        req_obj.status = 'rejected'
        req_obj.save()
        messages.info(request, f'Rejected product request for "{req_obj.name}".')
        return redirect('admin:shopapp_productrequest_changelist')

    def _process_approval(self, req_obj):
        model_map = {'product': Product, 'men': Men, 'women': Women}
        ModelClass = model_map.get(req_obj.category, Product)
        if req_obj.request_type == 'add':
            ModelClass.objects.create(
                name=req_obj.name,
                price=req_obj.price,
                discount=req_obj.discount,
                image=req_obj.image
            )
        elif req_obj.request_type == 'edit' and req_obj.target_id:
            target_obj = ModelClass.objects.filter(pk=req_obj.target_id).first()
            if target_obj:
                target_obj.name = req_obj.name
                target_obj.price = req_obj.price
                target_obj.discount = req_obj.discount
                if req_obj.image:
                    target_obj.image = req_obj.image
                target_obj.save()
        req_obj.status = 'approved'
        req_obj.save()

    @admin.action(description='Approve selected product requests')
    def approve_requests(self, request, queryset):
        count = 0
        for req_obj in queryset.filter(status='pending'):
            self._process_approval(req_obj)
            count += 1
        messages.success(request, f'Successfully approved {count} product request(s).')

    @admin.action(description='Reject selected product requests')
    def reject_requests(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='rejected')
        messages.info(request, f'Rejected {updated} product request(s).')


@admin.register(SubAdminRequest)
class SubAdminRequestAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'full_name', 'username', 'email', 'phone', 'status_badge', 'approve_reject_buttons', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('store_name', 'full_name', 'username', 'email', 'phone', 'reason')
    list_per_page = 20

    def status_badge(self, obj):
        colors = {'pending': '#e67e22', 'approved': '#27ae60', 'rejected': '#e74c3c'}
        color = colors.get(obj.status, '#7f8c8d')
        return format_html('<span style="background:{}; color:#fff; padding:3px 8px; border-radius:4px; font-weight:bold; font-size:11px; text-transform:uppercase;">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'

    def approve_reject_buttons(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a class="button" style="background:#27ae60; color:#fff; padding:4px 8px; border-radius:4px; font-weight:bold; text-decoration:none; margin-right:4px;" href="{}">Approve & Send Credentials</a>'
                '<a class="button" style="background:#e74c3c; color:#fff; padding:4px 8px; border-radius:4px; font-weight:bold; text-decoration:none;" href="{}">Reject</a>',
                f'approve-seller/{obj.pk}/',
                f'reject-seller/{obj.pk}/'
            )
        return mark_safe('<span style="color:#888;">Processed</span>')
    approve_reject_buttons.short_description = 'Actions'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('approve-seller/<int:req_id>/', self.admin_site.admin_view(self.approve_seller_request), name='subadminrequest-approve'),
            path('reject-seller/<int:req_id>/', self.admin_site.admin_view(self.reject_seller_request), name='subadminrequest-reject'),
        ]
        return custom_urls + urls

    def approve_seller_request(self, request, req_id):
        import random, string
        from django.core.mail import send_mail
        from django.conf import settings

        req_obj = get_object_or_404(SubAdminRequest, pk=req_id)
        
        user = User.objects.filter(username=req_obj.username).first()
        raw_password = 'SV-Seller#' + ''.join(random.choices(string.digits, k=6))
        
        if not user:
            user = User.objects.create_user(
                username=req_obj.username,
                email=req_obj.email,
                password=raw_password
            )
        else:
            user.set_password(raw_password)

        user.is_staff = True
        user.is_active = True
        user.first_name = req_obj.full_name
        user.save()

        req_obj.status = 'approved'
        req_obj.save()

        seller_login_url = request.build_absolute_uri('/seller/login/')

        subject = f"🎉 Approved: STYLEVERSE Sub-Admin Seller Portal Credentials"
        message = f"""Hello {req_obj.full_name},

Congratulations! Your application for a Sub-Admin (Seller) account for store '{req_obj.store_name}' on STYLEVERSE has been APPROVED by the Super Admin!

Your Sub-Admin Login Credentials:
--------------------------------------------------
Store Name: {req_obj.store_name}
Username  : {req_obj.username}
Password  : {raw_password}

Exclusive Seller Portal Login Link:
{seller_login_url}

Important Security Notice:
- Please click the link above to log in to the Seller Panel (/seller/login/).
- Customer accounts use the regular customer login page, while your Sub-Admin account uses the exclusive Seller Portal link provided above.
- We recommend changing your password after logging in for the first time.

Thank you,
STYLEVERSE Super Admin Team
"""
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[req_obj.email],
                fail_silently=False
            )
            messages.success(request, f'Approved seller "{req_obj.full_name}" ({req_obj.store_name})! Credentials and exclusive login link sent to {req_obj.email}.')
        except Exception as e:
            messages.warning(request, f'Approved seller account created, but email could not be sent: {e}')

        return redirect('admin:shopapp_subadminrequest_changelist')

    def reject_seller_request(self, request, req_id):
        req_obj = get_object_or_404(SubAdminRequest, pk=req_id)
        req_obj.status = 'rejected'
        req_obj.save()
        messages.info(request, f'Rejected seller application for "{req_obj.full_name}".')
        return redirect('admin:shopapp_subadminrequest_changelist')
