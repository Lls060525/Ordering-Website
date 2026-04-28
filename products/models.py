# products/models.py (Updated)
from django.db import models
from accounts.models import Vendor
from django.templatetags.static import static
class Product(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    # Changed from ForeignKey to CharField for free filling
    category = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Tech, Lifestyle, Gaming")
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return static('images/default_product.png')