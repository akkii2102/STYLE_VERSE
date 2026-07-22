from django.db import models
from django.contrib.auth.models import User
import os
from django.conf import settings


# ─────────────────────────────────────────────────────────
#  FORM & USER MODELS
# ─────────────────────────────────────────────────────────

class Contact(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    Name = models.CharField(max_length=50)
    Surname = models.CharField(max_length=50)
    Email = models.EmailField()
    Message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_review = models.TextField(blank=True, default='', help_text='Internal review & reply notes by Sub-Admin or Super-Admin')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_contacts')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.Name} {self.Surname} ({self.Email}) - {self.get_status_display()}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    bio = models.TextField()
    email = models.EmailField()
    birthdate = models.DateField(blank=True, null=True)
    contact = models.CharField(max_length=10)
    gender = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return f"{self.fname} {self.lname} ({self.email})"

class Registration(models.Model):
    firstname = models.CharField(max_length=255, null=True)
    lastname = models.CharField(max_length=255, null=True)
    email = models.EmailField(max_length=255, null=True)
    password = models.CharField(max_length=128, null=True)


# ─────────────────────────────────────────────────────────
#  PRODUCTS & CATEGORIES
# ─────────────────────────────────────────────────────────

class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.FloatField()
    discount = models.FloatField(default=0, help_text='Discount percentage (0-100)')
    image = models.ImageField(upload_to='Product')
    
    def get_discounted_price(self):
        """Calculate price after discount"""
        if self.discount > 0:
            return round(self.price * (1 - self.discount / 100), 2)
        return self.price

    @property
    def image_url(self):
        try:
            if not self.image:
                return ''
            full_path = os.path.join(settings.MEDIA_ROOT, str(self.image))
            if not os.path.exists(full_path):
                return ''
            return self.image.url
        except (ValueError, AttributeError):
            return ''

    @property
    def model_name(self):
        return 'product'

class Men(models.Model):
    name = models.CharField(max_length=50)
    price = models.FloatField()
    discount = models.FloatField(default=0, help_text='Discount percentage (0-100)')
    image = models.ImageField(upload_to='Product')
    
    def get_discounted_price(self):
        """Calculate price after discount"""
        if self.discount > 0:
            return round(self.price * (1 - self.discount / 100), 2)
        return self.price

    @property
    def image_url(self):
        try:
            if not self.image:
                return ''
            full_path = os.path.join(settings.MEDIA_ROOT, str(self.image))
            if not os.path.exists(full_path):
                return ''
            return self.image.url
        except (ValueError, AttributeError):
            return ''

    @property
    def model_name(self):
        return 'men'

class Women(models.Model):
    name = models.CharField(max_length=50)
    price = models.FloatField()
    discount = models.FloatField(default=0, help_text='Discount percentage (0-100)')
    image = models.ImageField(upload_to='Product')
    
    def get_discounted_price(self):
        """Calculate price after discount"""
        if self.discount > 0:
            return round(self.price * (1 - self.discount / 100), 2)
        return self.price

    @property
    def image_url(self):
        try:
            if not self.image:
                return ''
            full_path = os.path.join(settings.MEDIA_ROOT, str(self.image))
            if not os.path.exists(full_path):
                return ''
            return self.image.url
        except (ValueError, AttributeError):
            return ''

    @property
    def model_name(self):
        return 'women'


class Wishlist(models.Model):
    MODEL_CHOICES = [
        ('product', 'Product'),
        ('men', 'Men'),
        ('women', 'Women'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    model_type = models.CharField(max_length=20, choices=MODEL_CHOICES, default='product')
    object_id = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=100, blank=True, default='')
    price = models.FloatField(default=0)
    image_url = models.CharField(max_length=500, blank=True, default='')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'model_type', 'object_id')

    def __str__(self):
        return f"{self.user.username} → {self.name}"



# ─────────────────────────────────────────────────────────
#  ORDER SYSTEM
# ─────────────────────────────────────────────────────────

class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash_on_delivery', 'Cash on Delivery'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI / Google Pay'),
        ('net_banking', 'Net Banking'),
        ('paypal', 'PayPal'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    ORDER_STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number    = models.CharField(max_length=20, unique=True, blank=True)
    name            = models.CharField(max_length=100)
    email           = models.EmailField(max_length=100)
    phone           = models.CharField(max_length=20)
    address         = models.TextField()
    city            = models.CharField(max_length=100)
    state           = models.CharField(max_length=100)
    country         = models.CharField(max_length=100, default='India')
    pincode         = models.CharField(max_length=10)
    payment_method  = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='cash_on_delivery')
    payment_status  = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    status          = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='processing')
    subtotal        = models.FloatField(default=0)
    discount        = models.FloatField(default=0)
    shipping_cost   = models.FloatField(default=0)
    total_price     = models.FloatField(default=0)
    order_date      = models.DateTimeField(auto_now_add=True)
    updated_date    = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-order_date']

    def save(self, *args, **kwargs):
        if not self.order_number:
            import random, string
            self.order_number = 'SV-' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)

    @property
    def full_address(self):
        return f"{self.address}, {self.city}, {self.state}, {self.country} – {self.pincode}"

    def get_status_display(self):
        return dict(self.ORDER_STATUS_CHOICES).get(self.status, self.status)

    def get_payment_status_display(self):
        return dict(self.PAYMENT_STATUS_CHOICES).get(self.payment_status, self.payment_status)

    def get_payment_method_display(self):
        return dict(self.PAYMENT_METHOD_CHOICES).get(self.payment_method, self.payment_method)

    def __str__(self):
        return f"Order #{self.order_number} by {self.name}"


class OrderItem(models.Model):
    order        = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=200)
    brand_name   = models.CharField(max_length=100, default='STYLEVERSE')
    quantity     = models.PositiveIntegerField(default=1)
    unit_price   = models.FloatField()
    size         = models.CharField(max_length=10, blank=True)
    color        = models.CharField(max_length=30, blank=True)

    @property
    def sub_total(self):
        return round(self.unit_price * self.quantity, 2)

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"


# ─────────────────────────────────────────────────────────
#  PRODUCT APPROVAL REQUESTS (Sub Admin → Super Admin)
# ─────────────────────────────────────────────────────────

class ProductRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('add', 'Add Product'),
        ('edit', 'Edit Product'),
    ]
    CATEGORY_CHOICES = [
        ('product', 'General Product'),
        ('men', 'Men'),
        ('women', 'Women'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_requests')
    request_type = models.CharField(max_length=10, choices=REQUEST_TYPE_CHOICES, default='add')
    category     = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='product')
    target_id    = models.PositiveIntegerField(null=True, blank=True, help_text='ID of existing product if edit')
    name         = models.CharField(max_length=100)
    price        = models.FloatField()
    discount     = models.FloatField(default=0, help_text='Discount percentage (0-100)')
    image        = models.ImageField(upload_to='ProductRequest', null=True, blank=True)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at   = models.DateTimeField(auto_now_add=True)

    @property
    def image_url(self):
        try:
            return self.image.url if self.image else ''
        except (ValueError, AttributeError):
            return ''

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_request_type_display()} - {self.name} ({self.get_status_display()})"


# ─────────────────────────────────────────────────────────
#  SUPER ADMIN <-> SUB ADMIN INTERNAL DISCUSSIONS
# ─────────────────────────────────────────────────────────

class AdminDiscussion(models.Model):
    TYPE_CHOICES = [
        ('group', 'Group (All Sub-Admins)'),
        ('individual', 'Individual Sub-Admin'),
    ]
    sender          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_discussions')
    recipient       = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='received_discussions', help_text='Specific Sub-Admin if individual chat; null if Group')
    discussion_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='group')
    title           = models.CharField(max_length=200, help_text='Discussion Topic / Subject')
    message         = models.TextField()
    is_important    = models.BooleanField(default=False, help_text='Highlight topic for admins')
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        recip_str = self.recipient.username if self.recipient else "Group"
        return f"[{self.sender.username} → {recip_str}] {self.title}"


class AdminDiscussionReply(models.Model):
    discussion   = models.ForeignKey(AdminDiscussion, on_delete=models.CASCADE, related_name='replies')
    sender       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussion_replies')
    reply_text   = models.TextField()
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Reply by {self.sender.username} on '{self.discussion.title}'"


# ─────────────────────────────────────────────────────────
#  SUB-ADMIN / SELLER REGISTRATION REQUESTS
# ─────────────────────────────────────────────────────────

class SubAdminRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved (Credentials Sent)'),
        ('rejected', 'Rejected'),
    ]
    full_name   = models.CharField(max_length=100)
    username    = models.CharField(max_length=50)
    email       = models.EmailField()
    phone       = models.CharField(max_length=20)
    store_name  = models.CharField(max_length=100)
    reason      = models.TextField(help_text='Reason / Business details for applying as seller')
    status      = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Seller Request: {self.store_name} ({self.full_name}) - {self.get_status_display()}"
