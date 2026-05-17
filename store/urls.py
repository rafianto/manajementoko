from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Kategori
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Supplier
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/update/', views.supplier_update, name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),

    # Barang
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/update/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Rak
    path('shelves/', views.shelf_list, name='shelf_list'),
    path('shelves/create/', views.shelf_create, name='shelf_create'),
    path('shelves/<int:pk>/update/', views.shelf_update, name='shelf_update'),
    path('shelves/<int:pk>/delete/', views.shelf_delete, name='shelf_delete'),
    path('shelves/<int:pk>/', views.shelf_detail, name='shelf_detail'),
    path('shelves/<int:shelf_pk>/remove/<int:product_pk>/', views.shelf_product_remove, name='shelf_product_remove'),

    # Stok Masuk
    path('stock-in/', views.stockin_list, name='stockin_list'),
    path('stock-in/create/', views.stockin_create, name='stockin_create'),

    # POS
    path('pos/', views.pos, name='pos'),
    path('pos/process/', views.pos_process, name='pos_process'),
    path('pos/search/', views.product_search_api, name='product_search'),

    # Transaksi
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/<int:pk>/', views.transaction_detail, name='transaction_detail'),
    path('transactions/<int:pk>/receipt/', views.transaction_receipt, name='transaction_receipt'), # <--- TAMBAHKAN INI

    # Pengeluaran
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),

    # Pemasukan
    path('incomes/', views.income_list, name='income_list'),
    path('incomes/create/', views.income_create, name='income_create'),
    path('incomes/<int:pk>/delete/', views.income_delete, name='income_delete'),

    # Laporan
    path('reports/', views.report, name='report'),
]