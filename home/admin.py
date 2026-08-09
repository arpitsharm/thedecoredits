from django.contrib import admin
from .models import Product, ProductImage, Pricing, QuoteRequest, Review, Category


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'category', 'description', 'material', 'views_count', 'created_at')
    search_fields = ('sku', 'description', 'material')
    list_filter = ('category', 'material')
    inlines = [ProductImageInline]


@admin.register(Pricing)
class PricingAdmin(admin.ModelAdmin):
    list_display = ('product', 'moq', 'price')


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'product', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('full_name', 'phone_number')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'product', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('customer_name', 'comment')
