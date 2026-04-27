from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Customer, Vendor

class CustomerSignUpForm(UserCreationForm):
    # We add these specifically to ensure they appear and are required
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        # We explicitly list the fields we want to show in the HTML
        fields = ("username", "email", "first_name", "last_name")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_customer = True
        user.email = self.cleaned_data.get('email')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        if commit:
            user.save()
            Customer.objects.create(user=user)
        return user

class VendorSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    store_name = forms.CharField(max_length=255, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_seller = True
        user.email = self.cleaned_data.get('email')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        if commit:
            user.save()
            # We use the extra 'store_name' field from this specific form
            Vendor.objects.create(user=user, store_name=self.cleaned_data.get('store_name'))
        return user