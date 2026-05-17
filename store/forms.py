from django import forms
from django.forms import inlineformset_factory
from .models import (
    Category, Supplier, Product, Shelf, ShelfProduct,
    StockIn, Transaction, TransactionItem, Expense, Income
)

from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'barcode', 'category', 'description', 'unit',
                  'purchase_price', 'selling_price', 'image', 'is_active', 'minimum_stock']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nama barang'}),
            'sku': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'SKU-001'}),
            'barcode': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Barcode (opsional)'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'unit': forms.Select(attrs={'class': 'form-input'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'form-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-5 h-5'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['purchase_price'].widget.attrs.update({'style': 'padding-left: 2.5rem;'})
        self.fields['selling_price'].widget.attrs.update({'style': 'padding-left: 2.5rem;'})

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nama kategori'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Deskripsi (opsional)'}),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nama supplier'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nama kontak'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nomor telepon'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Alamat'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'barcode', 'category', 'description', 'unit',
                  'purchase_price', 'selling_price', 'image', 'is_active', 'minimum_stock']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nama barang'}),
            'sku': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'SKU-001'}),
            'barcode': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Barcode (opsional)'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'unit': forms.Select(attrs={'class': 'form-input'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'form-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-5 h-5'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-input'}),
        }


class ShelfForm(forms.ModelForm):
    class Meta:
        model = Shelf
        fields = ['name', 'location', 'description', 'capacity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nama rak'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Lokasi rak di toko'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'capacity': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '100'}),
        }


class ShelfProductForm(forms.ModelForm):
    class Meta:
        model = ShelfProduct
        fields = ['product', 'shelf', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-input'}),
            'shelf': forms.Select(attrs={'class': 'form-input'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input'}),
        }


class StockInForm(forms.ModelForm):
    class Meta:
        model = StockIn
        fields = ['product', 'supplier', 'quantity', 'purchase_price', 'shelf', 'date', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-input'}),
            'supplier': forms.Select(attrs={'class': 'form-input'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'shelf': forms.Select(attrs={'class': 'form-input'}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True)


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'category', 'description', 'amount']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Deskripsi pengeluaran'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
        }


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['date', 'category', 'description', 'amount']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Deskripsi pemasukan'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
        }


class ReportFilterForm(forms.Form):
    REPORT_TYPE = [
        ('daily', 'Harian'),
        ('weekly', 'Mingguan'),
        ('monthly', 'Bulanan'),
    ]
    report_type = forms.ChoiceField(choices=REPORT_TYPE, widget=forms.Select(attrs={'class': 'form-input'}))
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}))
    month = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 12}))
    year = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-input', 'min': 2020}))