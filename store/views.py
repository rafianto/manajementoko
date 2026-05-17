from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F, DecimalField, Count
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from datetime import timedelta
import json

from decimal import Decimal  # 

from .models import (
    Category, Supplier, Product, Shelf, ShelfProduct,
    StockIn, Transaction, TransactionItem, Expense, Income
)
from .forms import (
    CategoryForm, SupplierForm, ProductForm, ShelfForm,
    ShelfProductForm, StockInForm, ExpenseForm, IncomeForm, ReportFilterForm
)
from .utils import get_daily_stats, get_weekly_stats, get_monthly_stats

from .models import Product, Category, ShelfProduct, StockIn
from .forms import ProductForm

# ======================== BARANG DAGANGAN ========================

@login_required
def product_list(request):
    products = Product.objects.all().prefetch_related('shelf_placements__shelf', 'category')
    category_filter = request.GET.get('category')
    search = request.GET.get('search')
    stock_filter = request.GET.get('stock')

    if category_filter:
        products = products.filter(category_id=category_filter)
    if search:
        products = products.filter(name__icontains=search) | products.filter(sku__icontains=search) | products.filter(barcode__icontains=search)
    if stock_filter == 'low':
        low_ids = [p.id for p in Product.objects.all() if p.is_low_stock]
        products = products.filter(id__in=low_ids)

    categories = Category.objects.all()
    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
        'category_filter': category_filter,
        'search': search,
        'stock_filter': stock_filter,
    })


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    shelf_placements = ShelfProduct.objects.filter(product=product).select_related('shelf')
    stock_history = StockIn.objects.filter(product=product).select_related('supplier').order_by('-date')
    
    return render(request, 'store/product_detail.html', {
        'product': product,
        'shelf_placements': shelf_placements,
        'stock_history': stock_history,
    })


@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Barang berhasil ditambahkan!')
            return redirect('store:product_list')
    else:
        form = ProductForm()
    return render(request, 'store/product_form.html', {'form': form, 'title': 'Tambah Barang Baru'})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Barang berhasil diperbarui!')
            return redirect('store:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/product_form.html', {'form': form, 'title': 'Edit Barang'})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Barang berhasil dihapus!')
        return redirect('store:product_list')
    return render(request, 'store/product_confirm_delete.html', {'product': product})

# ======================== DASHBOARD ========================
@login_required
def dashboard(request):
    today = timezone.now().date()
    daily = get_daily_stats(today)

    # Produk stok rendah
    low_stock_products = []
    for p in Product.objects.filter(is_active=True):
        if p.is_low_stock:
            low_stock_products.append(p)

    # Statistik 7 hari terakhir
    last_7_days = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        stats = get_daily_stats(d)
        last_7_days.append(stats)

    # Total data
    total_products = Product.objects.filter(is_active=True).count()
    total_transactions_today = daily['total_transactions']
    total_shelves = Shelf.objects.count()

    context = {
        'daily': daily,
        'low_stock_products': low_stock_products,
        'last_7_days': last_7_days,
        'total_products': total_products,
        'total_transactions_today': total_transactions_today,
        'total_shelves': total_shelves,
    }
    return render(request, 'store/dashboard.html', context)


# ======================== KATEGORI ========================
@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'store/category_list.html', {'categories': categories})


@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori berhasil ditambahkan!')
            return redirect('store:category_list')
    else:
        form = CategoryForm()
    return render(request, 'store/category_form.html', {'form': form, 'title': 'Tambah Kategori'})


@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori berhasil diperbarui!')
            return redirect('store:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'store/category_form.html', {'form': form, 'title': 'Edit Kategori'})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Kategori berhasil dihapus!')
        return redirect('store:category_list')
    return render(request, 'store/category_form.html', {'title': 'Hapus Kategori', 'delete': True, 'object': category})


# ======================== SUPPLIER ========================
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'store/supplier_list.html', {'suppliers': suppliers})


@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier berhasil ditambahkan!')
            return redirect('store:supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'store/supplier_form.html', {'form': form, 'title': 'Tambah Supplier'})


@login_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier berhasil diperbarui!')
            return redirect('store:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'store/supplier_form.html', {'form': form, 'title': 'Edit Supplier'})


@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier berhasil dihapus!')
        return redirect('store:supplier_list')
    return render(request, 'store/supplier_form.html', {'title': 'Hapus Supplier', 'delete': True, 'object': supplier})


# ======================== BARANG DAGANGAN ========================
@login_required
def product_list(request):
    products = Product.objects.all()
    category_filter = request.GET.get('category')
    search = request.GET.get('search')
    stock_filter = request.GET.get('stock')

    if category_filter:
        products = products.filter(category_id=category_filter)
    if search:
        products = products.filter(name__icontains=search) | products.filter(sku__icontains=search)
    if stock_filter == 'low':
        # Filter produk dengan stok rendah
        low_ids = []
        for p in products:
            if p.is_low_stock:
                low_ids.append(p.id)
        products = products.filter(id__in=low_ids)

    categories = Category.objects.all()
    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
        'category_filter': category_filter,
        'search': search,
        'stock_filter': stock_filter,
    })


@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Barang berhasil ditambahkan!')
            return redirect('store:product_list')
    else:
        form = ProductForm()
    return render(request, 'store/product_form.html', {'form': form, 'title': 'Tambah Barang'})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Barang berhasil diperbarui!')
            return redirect('store:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/product_form.html', {'form': form, 'title': 'Edit Barang'})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Barang berhasil dihapus!')
        return redirect('store:product_list')
    return render(request, 'store/product_form.html', {'title': 'Hapus Barang', 'delete': True, 'object': product})


# ======================== RAK PAJANGAN ========================
@login_required
def shelf_list(request):
    shelves = Shelf.objects.all()
    return render(request, 'store/shelf_list.html', {'shelves': shelves})


@login_required
def shelf_create(request):
    if request.method == 'POST':
        form = ShelfForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rak berhasil ditambahkan!')
            return redirect('store:shelf_list')
    else:
        form = ShelfForm()
    return render(request, 'store/shelf_form.html', {'form': form, 'title': 'Tambah Rak'})


@login_required
def shelf_update(request, pk):
    shelf = get_object_or_404(Shelf, pk=pk)
    if request.method == 'POST':
        form = ShelfForm(request.POST, instance=shelf)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rak berhasil diperbarui!')
            return redirect('store:shelf_list')
    else:
        form = ShelfForm(instance=shelf)
    return render(request, 'store/shelf_form.html', {'form': form, 'title': 'Edit Rak'})


@login_required
def shelf_detail(request, pk):
    shelf = get_object_or_404(Shelf, pk=pk)
    shelf_products = ShelfProduct.objects.filter(shelf=shelf).select_related('product')

    if request.method == 'POST':
        form = ShelfProductForm(request.POST)
        if form.is_valid():
            sp = form.save(commit=False)
            sp.shelf = shelf
            # Cek apakah produk sudah ada di rak
            existing = ShelfProduct.objects.filter(product=sp.product, shelf=shelf).first()
            if existing:
                existing.quantity += sp.quantity
                existing.save()
                messages.success(request, f'Stok {sp.product.name} ditambahkan di rak ini!')
            else:
                sp.save()
                messages.success(request, f'{sp.product.name} ditambahkan ke rak!')
            return redirect('store:shelf_detail', pk=shelf.pk)
    else:
        form = ShelfProductForm(initial={'shelf': shelf})

    return render(request, 'store/shelf_detail.html', {
        'shelf': shelf,
        'shelf_products': shelf_products,
        'form': form,
    })


@login_required
def shelf_delete(request, pk):
    shelf = get_object_or_404(Shelf, pk=pk)
    if request.method == 'POST':
        shelf.delete()
        messages.success(request, 'Rak berhasil dihapus!')
        return redirect('store:shelf_list')
    return render(request, 'store/shelf_form.html', {'title': 'Hapus Rak', 'delete': True, 'object': shelf})


@login_required
def shelf_product_remove(request, shelf_pk, product_pk):
    sp = get_object_or_404(ShelfProduct, shelf_id=shelf_pk, product_id=product_pk)
    sp.delete()
    messages.success(request, 'Produk dihapus dari rak!')
    return redirect('store:shelf_detail', pk=shelf_pk)


# ======================== STOK MASUK ========================
@login_required
def stockin_list(request):
    stockins = StockIn.objects.select_related('product', 'supplier', 'shelf').all()

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    supplier = request.GET.get('supplier')

    if date_from:
        stockins = stockins.filter(date__gte=date_from)
    if date_to:
        stockins = stockins.filter(date__lte=date_to)
    if supplier:
        stockins = stockins.filter(supplier_id=supplier)

    suppliers = Supplier.objects.all()
    return render(request, 'store/stockin_list.html', {
        'stockins': stockins,
        'suppliers': suppliers,
    })


@login_required
def stockin_create(request):
    if request.method == 'POST':
        form = StockInForm(request.POST)
        if form.is_valid():
            stockin = form.save(commit=False)
            stockin.created_by = request.user
            stockin.save()
            messages.success(request, f'Stok masuk {stockin.product.name} x{stockin.quantity} berhasil dicatat!')
            return redirect('store:stockin_list')
    else:
        form = StockInForm(initial={'date': timezone.now().date()})
    return render(request, 'store/stockin_form.html', {'form': form, 'title': 'Stok Masuk Baru'})


# ======================== POINT OF SALES ========================
@login_required
def pos(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.all()
    return render(request, 'store/pos.html', {'products': products, 'categories': categories})


@login_required
@require_POST
def pos_process(request):
    """Proses transaksi POS via AJAX"""
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        payment_method = data.get('payment_method', 'cash')
        
        # KONVERSI KE DECIMAL SEGERA AGAR TIDAK CAMPUR DENGAN FLOAT
        discount = Decimal(str(data.get('discount', 0)))
        cash_received = Decimal(str(data.get('cash_received', 0)))
        customer_name = data.get('customer_name', '')

        if not items:
            return JsonResponse({'success': False, 'error': 'Tidak ada item!'})

        # Buat transaksi
        transaction = Transaction(
            payment_method=payment_method,
            discount=discount,
            customer_name=customer_name,
            created_by=request.user,
        )
        transaction.save()

        subtotal = Decimal('0.00')
        for item_data in items:
            product = Product.objects.get(id=item_data['product_id'])
            quantity = int(item_data['quantity'])
            price = Decimal(str(item_data['price'])) # Konversi ke Decimal

            # Cek stok
            if product.total_stock < quantity:
                transaction.delete()
                return JsonResponse({
                    'success': False,
                    'error': f'Stok {product.name} tidak cukup! Tersedia: {product.total_stock}'
                })

            ti = TransactionItem(
                transaction=transaction,
                product=product,
                product_name=product.name,
                quantity=quantity,
                price=price,
                cost_price=product.purchase_price, # Ini sudah Decimal dari DB
            )
            ti.save()
            subtotal += ti.subtotal

        # Update total transaksi (Semua variabel sudah Decimal)
        transaction.subtotal = subtotal
        transaction.total = subtotal - discount
        transaction.cash_received = cash_received
        transaction.change = max(cash_received - transaction.total, Decimal('0.00'))
        transaction.save()

        return JsonResponse({
            'success': True,
            'transaction_code': transaction.transaction_code,
            'total': str(transaction.total), # Konversi balik ke string untuk JSON
            'change': str(transaction.change),
        })

    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Produk tidak ditemukan!'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
# ======================== STRUK / INVOICE ========================
@login_required
def transaction_receipt(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    items = TransactionItem.objects.filter(transaction=transaction)
    
    context = {
        'transaction': transaction,
        'items': items,
        'store_name': 'Toko Guyangan Jaya', # Bisa Anda ganti sesuai nama toko
    }
    return render(request, 'store/transaction_receipt.html', context)    


@login_required
def transaction_list(request):
    transactions = Transaction.objects.all()
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from:
        transactions = transactions.filter(date__date__gte=date_from)
    if date_to:
        transactions = transactions.filter(date__date__lte=date_to)

    return render(request, 'store/transaction_list.html', {'transactions': transactions})


@login_required
def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    return render(request, 'store/transaction_detail.html', {'transaction': transaction})


# ======================== PENGELUARAN ========================
@login_required
def expense_list(request):
    expenses = Expense.objects.all()
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from:
        expenses = expenses.filter(date__gte=date_from)
    if date_to:
        expenses = expenses.filter(date__lte=date_to)

    total = expenses.aggregate(total=Coalesce(Sum('amount'), 0, output_field=DecimalField()))['total']
    return render(request, 'store/expense_list.html', {'expenses': expenses, 'total': total})


@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.save()
            messages.success(request, 'Pengeluaran berhasil dicatat!')
            return redirect('store:expense_list')
    else:
        form = ExpenseForm(initial={'date': timezone.now().date()})
    return render(request, 'store/expense_form.html', {'form': form, 'title': 'Catat Pengeluaran'})


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Pengeluaran berhasil dihapus!')
    return redirect('store:expense_list')


# ======================== PEMASUKAN ========================
@login_required
def income_list(request):
    incomes = Income.objects.all()
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from:
        incomes = incomes.filter(date__gte=date_from)
    if date_to:
        incomes = incomes.filter(date__lte=date_to)

    total = incomes.aggregate(total=Coalesce(Sum('amount'), 0, output_field=DecimalField()))['total']
    return render(request, 'store/income_list.html', {'incomes': incomes, 'total': total})


@login_required
def income_create(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.created_by = request.user
            income.save()
            messages.success(request, 'Pemasukan berhasil dicatat!')
            return redirect('store:income_list')
    else:
        form = IncomeForm(initial={'date': timezone.now().date()})
    return render(request, 'store/income_form.html', {'form': form, 'title': 'Catat Pemasukan'})


@login_required
def income_delete(request, pk):
    income = get_object_or_404(Income, pk=pk)
    if request.method == 'POST':
        income.delete()
        messages.success(request, 'Pemasukan berhasil dihapus!')
    return redirect('store:income_list')


# ======================== LAPORAN RUGI LABA ========================
@login_required
def report(request):
    report_type = request.GET.get('report_type', 'daily')
    today = timezone.now().date()

    context = {'report_type': report_type}

    if report_type == 'daily':
        date_str = request.GET.get('date')
        target_date = today
        if date_str:
            from datetime import datetime
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        stats = get_daily_stats(target_date)

        # Detail penjualan
        transactions = Transaction.objects.filter(date__date=target_date)
        expense_list = Expense.objects.filter(date=target_date)
        income_list = Income.objects.filter(date=target_date)

        context.update({
            'stats': stats,
            'transactions': transactions,
            'expense_list': expense_list,
            'income_list': income_list,
            'target_date': target_date,
        })

    elif report_type == 'weekly':
        from datetime import datetime
        start_str = request.GET.get('start_date')
        start_date = today - timedelta(days=today.weekday())
        if start_str:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()

        stats = get_weekly_stats(start_date)

        # Detail harian dalam minggu itu
        daily_details = []
        for i in range(7):
            d = start_date + timedelta(days=i)
            ds = get_daily_stats(d)
            ds['day_name'] = d.strftime('%A')
            daily_details.append(ds)

        context.update({
            'stats': stats,
            'daily_details': daily_details,
        })

    elif report_type == 'monthly':
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))

        stats = get_monthly_stats(year, month)

        # Detail mingguan dalam bulan
        from datetime import datetime
        import calendar
        _, days_in_month = calendar.monthrange(year, month)
        first_day = datetime(year, month, 1).date()
        last_day = datetime(year, month, days_in_month).date()

        # Detail per minggu
        weekly_details = []
        current = first_day
        week_num = 1
        while current <= last_day:
            week_end = min(current + timedelta(days=6), last_day)
            ws = {
                'week': f'Minggu {week_num}',
                'start': current,
                'end': week_end,
            }

            profit = TransactionItem.objects.filter(
                transaction__date__date__range=(current, week_end)
            ).aggregate(
                total=Coalesce(Sum('profit'), 0, output_field=DecimalField())
            )['total']

            sales = Transaction.objects.filter(
                date__date__range=(current, week_end)
            ).aggregate(
                total=Coalesce(Sum('total'), 0, output_field=DecimalField())
            )['total']

            expenses = Expense.objects.filter(
                date__range=(current, week_end)
            ).aggregate(
                total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
            )['total']

            ws['sales'] = sales
            ws['profit'] = profit
            ws['expenses'] = expenses
            ws['net'] = (profit or 0) - expenses
            weekly_details.append(ws)

            current = week_end + timedelta(days=1)
            week_num += 1

        context.update({
            'stats': stats,
            'weekly_details': weekly_details,
            'month': month,
            'year': year,
        })

    return render(request, 'store/report.html', context)


# ======================== API ENDPOINTS UNTUK POS ========================
@login_required
def product_search_api(request):
    """API pencarian produk untuk POS"""
    query = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True)
    if query:
        products = products.filter(name__icontains=query) | products.filter(sku__icontains=query) | products.filter(barcode__icontains=query)
    data = []
    for p in products[:20]:
        data.append({
            'id': p.id,
            'name': p.name,
            'sku': p.sku,
            'price': float(p.selling_price),
            'stock': p.total_stock,
            'unit': p.unit,
            'category': p.category.name if p.category else '-',
            'image': p.image.url if p.image else '',
        })
    return JsonResponse({'products': data})