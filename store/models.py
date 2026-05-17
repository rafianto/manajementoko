from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import uuid


# ======================== KATEGORI ========================
class Category(models.Model):
    name = models.CharField('Nama Kategori', max_length=100, unique=True)
    description = models.TextField('Deskripsi', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategori'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:category_list')


# ======================== SUPPLIER ========================
class Supplier(models.Model):
    name = models.CharField('Nama Supplier', max_length=200)
    contact_person = models.CharField('Kontak Person', max_length=150, blank=True, null=True)
    phone = models.CharField('Telepon', max_length=20, blank=True, null=True)
    email = models.EmailField('Email', blank=True, null=True)
    address = models.TextField('Alamat', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Supplier'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:supplier_list')


# ======================== RAK PAJANGAN ========================
class Shelf(models.Model):
    name = models.CharField('Nama Rak', max_length=100)
    location = models.CharField('Lokasi Rak', max_length=200, help_text='Contoh: Area depan kiri, Rak nomor 3')
    description = models.TextField('Deskripsi', blank=True, null=True)
    capacity = models.PositiveIntegerField('Kapasitas (unit)', default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Rak'
        verbose_name_plural = 'Rak'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.location}"

    def get_absolute_url(self):
        return reverse('store:shelf_list')

    @property
    def total_stock(self):
        return sum(sp.quantity for sp in self.shelf_products.all())

    @property
    def is_full(self):
        return self.total_stock >= self.capacity


# ======================== BARANG DAGANGAN ========================
class Product(models.Model):
    UNIT_CHOICES = [
        ('pcs', 'Pieces'),
        ('kg', 'Kilogram'),
        ('ltr', 'Liter'),
        ('pack', 'Pack'),
        ('box', 'Box'),
        ('lusin', 'Lusin'),
    ]

    name = models.CharField('Nama Barang', max_length=200)
    sku = models.CharField('Kode SKU', max_length=50, unique=True, help_text='Stock Keeping Unit')
    barcode = models.CharField('Barcode', max_length=100, blank=True, null=True, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name='Kategori', related_name='products')
    description = models.TextField('Deskripsi', blank=True, null=True)
    unit = models.CharField('Satuan', max_length=20, choices=UNIT_CHOICES, default='pcs')
    purchase_price = models.DecimalField('Harga Beli', max_digits=15, decimal_places=2, default=0)
    selling_price = models.DecimalField('Harga Jual', max_digits=15, decimal_places=2, default=0)
    image = models.ImageField('Gambar', upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField('Aktif', default=True)
    minimum_stock = models.PositiveIntegerField('Stok Minimum', default=5,
                                                 help_text='Peringatan stok rendah jika di bawah ini')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Barang'
        verbose_name_plural = 'Barang'
        ordering = ['name']

    def __str__(self):
        return f"{self.sku} - {self.name}"

    def get_absolute_url(self):
        return reverse('store:product_list')

    @property
    def total_stock(self):
        return sum(sp.quantity for sp in self.shelf_placements.all())

    @property
    def is_low_stock(self):
        return self.total_stock <= self.minimum_stock

    @property
    def profit_margin(self):
        if self.purchase_price > 0:
            return ((self.selling_price - self.purchase_price) / self.purchase_price) * 100
        return 0


# ======================== PENEMPATAN BARANG DI RAK ========================
class ShelfProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                 verbose_name='Barang', related_name='shelf_placements')
    shelf = models.ForeignKey(Shelf, on_delete=models.CASCADE,
                               verbose_name='Rak', related_name='shelf_products')
    quantity = models.PositiveIntegerField('Jumlah', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Penempatan Rak'
        verbose_name_plural = 'Penempatan Rak'
        unique_together = ['product', 'shelf']

    def __str__(self):
        return f"{self.product.name} di {self.shelf.name} ({self.quantity})"


# ======================== STOK MASUK ========================
class StockIn(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                 verbose_name='Barang', related_name='stock_ins')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True,
                                  verbose_name='Supplier', related_name='stock_ins')
    quantity = models.PositiveIntegerField('Jumlah Masuk')
    purchase_price = models.DecimalField('Harga Beli per Unit', max_digits=15, decimal_places=2)
    total_price = models.DecimalField('Total Harga', max_digits=15, decimal_places=2,
                                      help_text='Otomatis dihitung dari jumlah x harga beli')
    shelf = models.ForeignKey(Shelf, on_delete=models.SET_NULL, null=True,
                               verbose_name='Rak Tujuan', related_name='stock_ins')
    date = models.DateField('Tanggal Masuk')
    notes = models.TextField('Catatan', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Stok Masuk'
        verbose_name_plural = 'Stok Masuk'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"Masuk: {self.product.name} x{self.quantity} ({self.date})"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.purchase_price
        super().save(*args, **kwargs)


# ======================== TRANSAKSI POS ========================
class Transaction(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Tunai'),
        ('debit', 'Kartu Debit'),
        ('credit', 'Kartu Kredit'),
        ('qris', 'QRIS'),
        ('transfer', 'Transfer Bank'),
    ]

    transaction_code = models.CharField('Kode Transaksi', max_length=50, unique=True, editable=False)
    date = models.DateTimeField('Tanggal', auto_now_add=True)
    payment_method = models.CharField('Metode Pembayaran', max_length=20,
                                      choices=PAYMENT_METHOD_CHOICES, default='cash')
    subtotal = models.DecimalField('Subtotal', max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField('Diskon', max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=15, decimal_places=2, default=0)
    cash_received = models.DecimalField('Uang Diterima', max_digits=15, decimal_places=2, default=0)
    change = models.DecimalField('Kembalian', max_digits=15, decimal_places=2, default=0)
    customer_name = models.CharField('Nama Pelanggan', max_length=200, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField('Catatan', blank=True, null=True)

    class Meta:
        verbose_name = 'Transaksi'
        verbose_name_plural = 'Transaksi'
        ordering = ['-date']

    def __str__(self):
        return self.transaction_code

    def save(self, *args, **kwargs):
        if not self.transaction_code:
            self.transaction_code = f"TRX-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE,
                                     verbose_name='Transaksi', related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True,
                                 verbose_name='Barang')
    product_name = models.CharField('Nama Barang', max_length=200)
    quantity = models.PositiveIntegerField('Jumlah')
    price = models.DecimalField('Harga Satuan', max_digits=15, decimal_places=2)
    cost_price = models.DecimalField('Harga Modal', max_digits=15, decimal_places=2, default=0)
    subtotal = models.DecimalField('Subtotal', max_digits=15, decimal_places=2, default=0)
    profit = models.DecimalField('Keuntungan', max_digits=15, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Item Transaksi'
        verbose_name_plural = 'Item Transaksi'

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.price
        self.profit = self.quantity * (self.price - self.cost_price)
        super().save(*args, **kwargs)


# ======================== PENGELUARAN ========================
class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('operasional', 'Operasional'),
        ('gaji', 'Gaji Karyawan'),
        ('sewa', 'Sewa Tempat'),
        ('listrik', 'Listrik & Air'),
        ('transport', 'Transportasi'),
        ('perawatan', 'Perawatan'),
        ('lainnya', 'Lainnya'),
    ]

    date = models.DateField('Tanggal')
    category = models.CharField('Kategori', max_length=50, choices=CATEGORY_CHOICES, default='operasional')
    description = models.CharField('Deskripsi', max_length=300)
    amount = models.DecimalField('Jumlah', max_digits=15, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pengeluaran'
        verbose_name_plural = 'Pengeluaran'
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_category_display()} - {self.description} ({self.amount})"


# ======================== PEMASUKAN NON-PENJUALAN ========================
class Income(models.Model):
    CATEGORY_CHOICES = [
        ('jasa', 'Pendapatan Jasa'),
        ('sewa', 'Pendapatan Sewa'),
        ('lainnya', 'Lainnya'),
    ]

    date = models.DateField('Tanggal')
    category = models.CharField('Kategori', max_length=50, choices=CATEGORY_CHOICES, default='lainnya')
    description = models.CharField('Deskripsi', max_length=300)
    amount = models.DecimalField('Jumlah', max_digits=15, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pemasukan'
        verbose_name_plural = 'Pemasukan'
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_category_display()} - {self.description} ({self.amount})"
    