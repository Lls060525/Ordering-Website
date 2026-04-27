# products/models.py (Updated)
from django.db import models
from accounts.models import Vendor
from django.templatetags.static import static # Add this import

class Product(models.Model):
    # CHANGE THIS LINE: Replace OneToOneField with ForeignKey
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    # If you added the image field from the previous step, keep it here
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return self.name
    # HELPER METHOD for safer rendering
    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return static('images/default_product.png') # Ensure you have a default placeholder