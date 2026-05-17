from django.contrib import admin
from .models import (
    Category, Supplier, Product, Shelf, ShelfProduct,
    StockIn, Transaction, TransactionItem, Expense, Income
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'email']
    search_fields = ['name', 'contact_person']
    list_filter = ['name']


class ShelfProductInline(admin.TabularInline):
    model = ShelfProduct
    extra = 1


@admin.register(Shelf)
class ShelfAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'capacity', 'total_stock']
    inlines = [ShelfProductInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'category', 'unit', 'purchase_price', 'selling_price', 'total_stock', 'is_active']
    list_filter = ['category', 'unit', 'is_active']
    search_fields = ['name', 'sku', 'barcode']
    list_editable = ['selling_price']


@admin.register(StockIn)
class StockInAdmin(admin.ModelAdmin):
    list_display = ['product', 'supplier', 'quantity', 'purchase_price', 'total_price', 'shelf', 'date']
    list_filter = ['date', 'supplier']
    search_fields = ['product__name']


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 0
    readonly_fields = ['subtotal', 'profit']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_code', 'date', 'payment_method', 'total', 'total_items', 'created_by']
    list_filter = ['date', 'payment_method']
    search_fields = ['transaction_code', 'customer_name']
    inlines = [TransactionItemInline]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['date', 'category', 'description', 'amount']
    list_filter = ['date', 'category']


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['date', 'category', 'description', 'amount']
    list_filter = ['date', 'category']