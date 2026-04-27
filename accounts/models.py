from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# 1. Custom User Model
class User(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)
    
    # These fields are already in AbstractUser, but here is how you override them properly:
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)

    USERNAME_FIELD = 'email'  # Use email as the login ID
    REQUIRED_FIELDS = ['username']  # Email is already required by default now

    def __str__(self):
        return self.username

# 2. Customer Side
class Customer(models.Model):
    # Links to the Custom User
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='customer_profile')
    address = models.TextField(_("Shipping Address"), blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"Customer: {self.user.username}"

# 3. Seller / Vendor Side
class Vendor(models.Model):
    # Links to the Custom User
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='vendor_profile')
    store_name = models.CharField(_("Store Name"), max_length=255)
    description = models.TextField(_("Store Description"), blank=True)
    is_approved = models.BooleanField(default=False) # Admin can use this to verify sellers

    def __str__(self):
        return self.store_name