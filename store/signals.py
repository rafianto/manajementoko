from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StockIn, ShelfProduct, TransactionItem


@receiver(post_save, sender=StockIn)
def update_stock_on_stockin(sender, instance, created, **kwargs):
    """Tambah stok ke rak saat stok masuk disimpan"""
    if created:
        shelf = instance.shelf
        product = instance.product
        if shelf:
            sp, created = ShelfProduct.objects.get_or_create(
                product=product,
                shelf=shelf,
                defaults={'quantity': instance.quantity}
            )
            if not created:
                sp.quantity += instance.quantity
                sp.save()


@receiver(post_save, sender=TransactionItem)
def reduce_stock_on_sale(sender, instance, created, **kwargs):
    """Kurangi stok saat barang terjual"""
    if created and instance.product:
        # Cari rak yang memiliki produk ini, kurangi dari rak pertama yang ada stoknya
        shelf_products = ShelfProduct.objects.filter(
            product=instance.product,
            quantity__gt=0
        ).order_by('quantity')

        remaining = instance.quantity
        for sp in shelf_products:
            if remaining <= 0:
                break
            if sp.quantity >= remaining:
                sp.quantity -= remaining
                sp.save()
                remaining = 0
            else:
                remaining -= sp.quantity
                sp.quantity = 0
                sp.save()