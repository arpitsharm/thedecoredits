from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PhoneNumber(models.Model):
    label = models.CharField(max_length=100, help_text="e.g. Sales, Support, Owner")
    number = models.CharField(max_length=15)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.label} - {self.number}"

    def save(self, *args, **kwargs):
        if self.is_default:
            PhoneNumber.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Product(models.Model):
    sku = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    dimensions = models.CharField(max_length=200, blank=True)
    material = models.CharField(max_length=200, blank=True)
    colors_variants = models.CharField(max_length=500, blank=True, help_text="Comma separated colors/variants")
    weight = models.CharField(max_length=100, blank=True)
    packaging = models.CharField(max_length=300, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, help_text="WhatsApp number for quotes")
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sku} - {self.description[:50]}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.product.sku} - Image {self.order}"


class Pricing(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='pricings')
    moq = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"MOQ {self.moq} = Rs.{self.price}"


class QuoteRequest(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='quote_requests')
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.product.sku}"


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer_name = models.CharField(max_length=200)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer_name} - {self.product.sku} ({self.rating}/5)"

    @property
    def stars(self):
        return range(self.rating)
