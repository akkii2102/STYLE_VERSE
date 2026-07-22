from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from shopapp.models import UserProfile, SubAdminRequest


class SubAdminRequestForm(forms.ModelForm):
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'sv-input', 'placeholder': 'Your Full Name'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'sv-input', 'placeholder': 'Desired Username'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'sv-input', 'placeholder': 'Personal Email Address'})
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'sv-input', 'placeholder': '+91 98765 43210'})
    )
    store_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'sv-input', 'placeholder': 'Store / Business Name'})
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'sv-input', 'rows': 3, 'placeholder': 'Describe your business or reason for requesting a seller account'})
    )

    class Meta:
        model = SubAdminRequest
        fields = ['full_name', 'username', 'email', 'phone', 'store_name', 'reason']


class RegisterUserForm(UserCreationForm):
    ACCOUNT_TYPE_CHOICES = [
        ('customer', 'Customer / Buyer'),
        ('sub_admin', 'Sub-Admin / Seller'),
    ]
    account_type = forms.ChoiceField(
        choices=ACCOUNT_TYPE_CHOICES,
        initial='customer',
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'id_account_type'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'sv-input',
            'placeholder': 'Choose a username',
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'sv-input',
            'placeholder': 'Your email address',
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'sv-input',
            'placeholder': 'Create a password',
            'id': 'id_password1',
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'sv-input',
            'placeholder': 'Confirm your password',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        account_type = self.cleaned_data.get('account_type', 'customer')
        if account_type == 'sub_admin':
            user.is_staff = True
        else:
            user.is_staff = False
        if commit:
            user.save()
        return user


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'sv-input',
            'placeholder': 'Enter your username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'sv-input',
            'placeholder': 'Enter your password',
            'id': 'id_login_password',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'password']


class UserProfileForm(forms.ModelForm):
    fname = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'sv-input', 'placeholder': 'First name'})
    )
    lname = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'sv-input', 'placeholder': 'Last name'})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'sv-input', 'rows': 3, 'placeholder': 'Tell us about yourself'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'sv-input', 'placeholder': 'Email address'})
    )
    birthdate = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'sv-input', 'type': 'date'})
    )
    contact = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'sv-input', 'placeholder': 'Phone number'})
    )
    gender = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'sv-input', 'placeholder': 'Gender'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'sv-input', 'rows': 3, 'placeholder': 'Your address'})
    )

    class Meta:
        model = UserProfile
        fields = ('fname', 'lname', 'bio', 'email', 'birthdate', 'contact', 'gender', 'address')


class CheckoutForm(forms.Form):
    PAYMENT_CHOICES = [
        ('cash_on_delivery', 'Cash on Delivery'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI / Google Pay'),
        ('net_banking', 'Net Banking'),
        ('paypal', 'PayPal'),
    ]

    firstname = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'sv-input', 'placeholder': 'Full Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'sv-input', 'placeholder': 'Email Address'})
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'sv-input', 'placeholder': '+91 98765 43210'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'sv-input', 'placeholder': 'Street Address', 'rows': 3})
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'sv-input', 'placeholder': 'City'})
    )
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'sv-input', 'placeholder': 'State'})
    )
    country = forms.CharField(
        max_length=100,
        initial='India',
        widget=forms.TextInput(attrs={'class': 'sv-input', 'placeholder': 'Country'})
    )
    pincode = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'sv-input', 'placeholder': 'PIN Code'})
    )
    method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'sv-input'})
    )
