from django.contrib import admin

from .models import Product, Sale


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "size", "price", "stock", "low_at"]
    list_filter = ["category"]
    search_fields = ["name"]


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ["name_snapshot", "qty", "unit_price", "total", "created_at"]
    date_hierarchy = "created_at"
