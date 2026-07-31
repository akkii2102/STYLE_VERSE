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
    list_display = ('name', 'price', 'discount', 'get_discounted_price', 'added_by_seller', 'image')
    search_fields = ('name', 'created_by__username')
    list_filter = ('created_by', 'discount')
    fieldsets = (
        ('Product & Seller Assignment', {
            'fields': ('name', 'image', 'created_by'),
            'description': 'Select which Sub-Admin / Seller owns this product.'
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'discount', 'stock'),
            'description': 'Set the price and discount percentage (0-100)'
        }),
    )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "created_by":
            from django.db.models import Q
            kwargs["queryset"] = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True))
            kwargs["label"] = "Sub-Admin / Seller Username"
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_discounted_price(self, obj):
        return f"₹{obj.get_discounted_price()}"
    get_discounted_price.short_description = 'Final Price'

    def added_by_seller(self, obj):
        if obj.created_by:
            return format_html('<span style="background:#27ae60; color:#fff; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:12px; white-space:nowrap; display:inline-block;">🏪 @{}</span>', obj.created_by.username)
        return mark_safe('<span style="background:#7f8c8d; color:#fff; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:12px; white-space:nowrap; display:inline-block;">🛡️ Super Admin</span>')
    added_by_seller.short_description = 'Sub-Admin Username'


@admin.register(Men)
class MenAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount', 'get_discounted_price', 'added_by_seller', 'image')
    search_fields = ('name', 'created_by__username')
    list_filter = ('created_by', 'discount')
    fieldsets = (
        ('Product & Seller Assignment', {
            'fields': ('name', 'image', 'created_by'),
            'description': 'Select which Sub-Admin / Seller owns this product.'
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'discount', 'stock'),
            'description': 'Set the price and discount percentage (0-100)'
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "created_by":
            from django.db.models import Q
            kwargs["queryset"] = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True))
            kwargs["label"] = "Sub-Admin / Seller Username"
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_discounted_price(self, obj):
        return f"₹{obj.get_discounted_price()}"
    get_discounted_price.short_description = 'Final Price'

    def added_by_seller(self, obj):
        if obj.created_by:
            return format_html('<span style="background:#27ae60; color:#fff; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:12px; white-space:nowrap; display:inline-block;">🏪 @{}</span>', obj.created_by.username)
        return mark_safe('<span style="background:#7f8c8d; color:#fff; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:12px; white-space:nowrap; display:inline-block;">🛡️ Super Admin</span>')
    added_by_seller.short_description = 'Sub-Admin Username'


@admin.register(Women)
class WomenAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount', 'get_discounted_price', 'added_by_seller', 'image')
    search_fields = ('name', 'created_by__username')
    list_filter = ('created_by', 'discount')
    fieldsets = (
        ('Product & Seller Assignment', {
            'fields': ('name', 'image', 'created_by'),
            'description': 'Select which Sub-Admin / Seller owns this product.'
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'discount', 'stock'),
            'description': 'Set the price and discount percentage (0-100)'
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "created_by":
            from django.db.models import Q
            kwargs["queryset"] = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True))
            kwargs["label"] = "Sub-Admin / Seller Username"
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_discounted_price(self, obj):
        return f"₹{obj.get_discounted_price()}"
    get_discounted_price.short_description = 'Final Price'

    def added_by_seller(self, obj):
        if obj.created_by:
            return format_html('<span style="background:#27ae60; color:#fff; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:12px; white-space:nowrap; display:inline-block;">🏪 @{}</span>', obj.created_by.username)
        return mark_safe('<span style="background:#7f8c8d; color:#fff; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:12px; white-space:nowrap; display:inline-block;">🛡️ Super Admin</span>')
    added_by_seller.short_description = 'Sub-Admin Username'



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
    list_display = ('name', 'request_type_badge', 'category', 'price_display', 'sub_admin_username', 'status_badge', 'approve_reject_buttons', 'created_at')
    list_filter = ('status', 'request_type', 'category', 'user')
    search_fields = ('name', 'user__username')
    list_per_page = 20
    actions = ['approve_requests', 'reject_requests']

    def sub_admin_username(self, obj):
        if obj.user:
            return format_html('<span style="background:#27ae60; color:#fff; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:11px; white-space:nowrap; display:inline-block;">🏪 @{}</span>', obj.user.username)
        return mark_safe('<span style="color:#888;">-</span>')
    sub_admin_username.short_description = 'Sub-Admin Username'

    def request_type_badge(self, obj):
        color = '#3498db' if obj.request_type == 'add' else '#f1c40f'
        return format_html('<span style="background:{}; color:#fff; padding:4px 8px; border-radius:12px; font-weight:bold; font-size:11px; text-transform:uppercase; white-space:nowrap; display:inline-block;">{}</span>', color, obj.get_request_type_display())
    request_type_badge.short_description = 'Type'

    def status_badge(self, obj):
        colors = {'pending': '#e67e22', 'approved': '#27ae60', 'rejected': '#e74c3c'}
        color = colors.get(obj.status, '#7f8c8d')
        return format_html('<span style="background:{}; color:#fff; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:11px; text-transform:uppercase; white-space:nowrap; display:inline-block;">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'

    def price_display(self, obj):
        if obj.discount > 0:
            return format_html('₹{} <small style="color:#e74c3c;">({}% off)</small>', obj.price, int(obj.discount))
        return f"₹{obj.price}"
    price_display.short_description = 'Price'

    def approve_reject_buttons(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<div style="display:flex; gap:6px; white-space:nowrap;">'
                '<a class="button" style="background:#27ae60; color:#fff; padding:5px 10px; border-radius:6px; font-weight:bold; text-decoration:none; font-size:11px; display:inline-flex; align-items:center;" href="{}">Approve</a>'
                '<a class="button" style="background:#e74c3c; color:#fff; padding:5px 10px; border-radius:6px; font-weight:bold; text-decoration:none; font-size:11px; display:inline-flex; align-items:center;" href="{}">Reject</a>'
                '</div>',
                f'approve/{obj.pk}/',
                f'reject/{obj.pk}/'
            )
        return mark_safe('<span style="color:#888; font-weight:bold; text-transform:uppercase; font-size:11px;">Processed</span>')
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
                image=req_obj.image,
                created_by=req_obj.user
            )
        elif req_obj.request_type == 'edit' and req_obj.target_id:
            target_obj = ModelClass.objects.filter(pk=req_obj.target_id).first()
            if target_obj:
                target_obj.name = req_obj.name
                target_obj.price = req_obj.price
                target_obj.discount = req_obj.discount
                if req_obj.image:
                    target_obj.image = req_obj.image
                if not target_obj.created_by:
                    target_obj.created_by = req_obj.user
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
    list_display = ('store_name_display', 'full_name_display', 'username', 'email_display', 'phone_display', 'status_badge', 'approve_reject_buttons', 'created_at_display')
    list_filter = ('status', 'created_at')
    search_fields = ('store_name', 'full_name', 'username', 'email', 'phone', 'reason')
    list_per_page = 20

    def store_name_display(self, obj):
        return format_html('<strong style="white-space:nowrap;">{}</strong>', obj.store_name)
    store_name_display.short_description = 'Store Name'

    def full_name_display(self, obj):
        return format_html('<span style="white-space:nowrap;">{}</span>', obj.full_name or '-')
    full_name_display.short_description = 'Full Name'

    def email_display(self, obj):
        return format_html('<span style="white-space:nowrap; font-family:monospace; font-size:12px;">{}</span>', obj.email)
    email_display.short_description = 'Email'

    def phone_display(self, obj):
        return format_html('<span style="white-space:nowrap; font-family:monospace; font-size:12px;">{}</span>', obj.phone or '-')
    phone_display.short_description = 'Phone'

    def created_at_display(self, obj):
        return format_html('<span style="white-space:nowrap; font-size:12px;">{}</span>', obj.created_at.strftime('%b %d, %Y, %H:%M') if obj.created_at else '-')
    created_at_display.short_description = 'Created At'

    def status_badge(self, obj):
        colors = {'pending': '#e67e22', 'approved': '#27ae60', 'rejected': '#e74c3c'}
        color = colors.get(obj.status, '#7f8c8d')
        return format_html(
            '<span style="background:{}; color:#fff; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:11px; text-transform:uppercase; white-space:nowrap; display:inline-block;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def approve_reject_buttons(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<div style="display:flex; gap:6px; white-space:nowrap;">'
                '<a class="button" style="background:#27ae60; color:#fff; padding:5px 10px; border-radius:6px; font-weight:bold; text-decoration:none; font-size:11px; display:inline-flex; align-items:center;" href="{}">Approve & Send Credentials</a>'
                '<a class="button" style="background:#e74c3c; color:#fff; padding:5px 10px; border-radius:6px; font-weight:bold; text-decoration:none; font-size:11px; display:inline-flex; align-items:center;" href="{}">Reject</a>'
                '</div>',
                f'approve-seller/{obj.pk}/',
                f'reject-seller/{obj.pk}/'
            )
        return format_html('<span style="color:#888; font-weight:bold; text-transform:uppercase; font-size:11px;">Processed</span>')
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
        from django.core.mail import EmailMultiAlternatives
        from django.conf import settings

        req_obj = get_object_or_404(SubAdminRequest, pk=req_id)
        
        user = User.objects.filter(username=req_obj.username).first()
        raw_password = req_obj.requested_password if req_obj.requested_password else ('SV-Seller#' + ''.join(random.choices(string.digits, k=6)))
        
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

        # Recipients: seller + all superadmins with email set
        superusers = User.objects.filter(is_superuser=True, is_active=True)
        recipient_emails = list(set(
            [u.email for u in superusers if u.email] + ([req_obj.email] if req_obj.email else [])
        ))
        if not recipient_emails:
            recipient_emails = [settings.EMAIL_HOST_USER]

        subject = f'🎉 [STYLEVERSE] Seller Account Approved — {req_obj.store_name}'

        plain_message = f"""Hello {req_obj.full_name},

Congratulations! Your Sub-Admin (Seller) account for '{req_obj.store_name}' on STYLEVERSE has been APPROVED.

Store Name : {req_obj.store_name}
Username   : {req_obj.username}
Password   : {raw_password}

The Super Admin will send you a secure login link to your registered email when access is granted.

Thank you,
STYLEVERSE Super Admin Team
"""
        store_initial = (req_obj.store_name[:2] if req_obj.store_name else 'SV').upper()
        html_message = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Seller Account Approved</title></head>
<body style="margin:0;padding:0;background:#F6F4EF;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;color:#1B2420;">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#F6F4EF;padding:40px 20px;">
  <tr><td align="center">
    <table width="560" cellpadding="0" cellspacing="0" border="0" style="max-width:560px;width:100%;border-radius:16px;overflow:hidden;box-shadow:0 4px 32px rgba(27,36,32,.12);">
      <tr><td style="background:#1B2420;padding:32px 40px;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td><table cellpadding="0" cellspacing="0" border="0"><tr>
              <td style="width:42px;height:42px;background:#E7DAC0;border-radius:50%;text-align:center;vertical-align:middle;font-family:monospace;font-weight:700;font-size:14px;color:#1B2420;">SV</td>
              <td style="padding-left:12px;"><div style="font-size:18px;font-weight:700;color:#EFEAE0;">STYLEVERSE</div><div style="font-family:monospace;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#8C978F;">SUPER ADMIN PORTAL</div></td>
            </tr></table></td>
            <td align="right"><span style="background:rgba(46,89,64,.5);border:1px solid rgba(100,180,120,.3);border-radius:999px;padding:5px 12px;font-family:monospace;font-size:10px;font-weight:700;text-transform:uppercase;color:#A8D8B4;">✅ APPROVED</span></td>
          </tr>
        </table>
        <div style="margin-top:28px;">
          <div style="font-size:26px;font-weight:700;color:#EFEAE0;line-height:1.25;margin-bottom:10px;">Congratulations,<br>{req_obj.full_name}!</div>
          <div style="font-size:13.5px;color:#9BA69D;line-height:1.6;">Your Sub-Admin (Seller) account on STYLEVERSE has been approved by the Super Admin.</div>
        </div>
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:24px;background:rgba(231,218,192,.07);border:1px solid rgba(231,218,192,.18);border-radius:12px;padding:16px 18px;">
          <tr>
            <td style="width:44px;height:44px;background:#2E5940;border-radius:50%;text-align:center;vertical-align:middle;font-family:monospace;font-weight:700;font-size:14px;color:#fff;">{store_initial}</td>
            <td style="padding-left:12px;"><div style="font-size:14px;font-weight:600;color:#EFEAE0;">{req_obj.store_name}</div><div style="font-family:monospace;font-size:11px;color:#8C978F;">{req_obj.email}</div></td>
          </tr>
        </table>
      </td></tr>
      <tr><td style="background:#FFFFFF;padding:36px 40px;">
        <div style="font-family:monospace;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#2E5940;font-weight:700;margin-bottom:20px;">YOUR ACCOUNT CREDENTIALS</div>
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border:1px solid #E4E0D6;border-radius:10px;overflow:hidden;margin-bottom:24px;">
          <tr style="background:#F6F4EF;"><td style="padding:12px 18px;font-size:12px;font-family:monospace;font-weight:700;color:#5B6560;text-transform:uppercase;border-bottom:1px solid #E4E0D6;width:35%;">Store</td><td style="padding:12px 18px;font-size:13.5px;color:#1B2420;border-bottom:1px solid #E4E0D6;font-weight:600;">{req_obj.store_name}</td></tr>
          <tr><td style="padding:12px 18px;font-size:12px;font-family:monospace;font-weight:700;color:#5B6560;text-transform:uppercase;border-bottom:1px solid #E4E0D6;">Username</td><td style="padding:12px 18px;font-size:13.5px;color:#1B2420;border-bottom:1px solid #E4E0D6;font-family:monospace;font-weight:600;">{req_obj.username}</td></tr>
          <tr style="background:#F6F4EF;"><td style="padding:12px 18px;font-size:12px;font-family:monospace;font-weight:700;color:#5B6560;text-transform:uppercase;">Password</td><td style="padding:12px 18px;font-size:13.5px;color:#1B2420;font-family:monospace;font-weight:600;">{raw_password}</td></tr>
        </table>
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#E4EEE8;border:1px solid #D8EAD9;border-radius:10px;padding:14px 18px;margin-bottom:24px;">
          <tr><td style="font-size:12.5px;color:#2E5940;line-height:1.6;"><strong>🔐 Next Steps</strong><br>The Super Admin will send a <strong>secure login link</strong> to your registered email when access is granted. Keep your credentials safe.</td></tr>
        </table>
        <div style="font-size:12px;color:#9BA69D;line-height:1.6;">If you did not apply, contact us at <a href="mailto:{settings.EMAIL_HOST_USER}" style="color:#2E5940;">{settings.EMAIL_HOST_USER}</a>.</div>
      </td></tr>
      <tr><td style="background:#1B2420;padding:16px 40px;text-align:center;"><div style="font-family:monospace;font-size:10.5px;color:#5B6560;">&copy; 2026 STYLEVERSE &mdash; Super Admin Access Only</div></td></tr>
    </table>
  </td></tr>
</table>
</body></html>"""

        try:
            email_msg = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                to=recipient_emails,
            )
            email_msg.attach_alternative(html_message, "text/html")
            email_msg.send(fail_silently=False)
            messages.success(request, f'✅ Approved "{req_obj.full_name}" ({req_obj.store_name})! Credentials sent to {req_obj.email}.')
        except Exception as e:
            messages.warning(request, f'Seller account approved, but email could not be sent: {e}')

        return redirect('admin:shopapp_subadminrequest_changelist')

    def reject_seller_request(self, request, req_id):
        req_obj = get_object_or_404(SubAdminRequest, pk=req_id)
        req_obj.status = 'rejected'
        req_obj.save()
        messages.info(request, f'Rejected seller application for "{req_obj.full_name}".')
        return redirect('admin:shopapp_subadminrequest_changelist')


from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'full_name_display', 'user_role_badge', 'is_active', 'date_joined')
    list_filter = ('is_superuser', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    list_per_page = 25

    def full_name_display(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return format_html('<span style="white-space:nowrap;">{}</span>', name if name else '-')
    full_name_display.short_description = 'Full Name'

    def user_role_badge(self, obj):
        if obj.is_superuser:
            return mark_safe(
                '<span style="background:#8e44ad; color:#fff; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:11px; text-transform:uppercase; white-space:nowrap; display:inline-block;">'
                '👑 SUPER ADMIN</span>'
            )
        elif obj.is_staff:
            return mark_safe(
                '<span style="background:#27ae60; color:#fff; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:11px; text-transform:uppercase; white-space:nowrap; display:inline-block;">'
                '🏪 SUB ADMIN / SELLER</span>'
            )
        else:
            return mark_safe(
                '<span style="background:#2980b9; color:#fff; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:11px; text-transform:uppercase; white-space:nowrap; display:inline-block;">'
                '👤 REGULAR CUSTOMER</span>'
            )
    user_role_badge.short_description = 'Account Role / Type'
