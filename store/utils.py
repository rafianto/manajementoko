from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from .models import Transaction, TransactionItem, Expense, Income


def get_daily_stats(date=None):
    """Mendapatkan statistik harian"""
    if date is None:
        date = timezone.now().date()

    # Penjualan hari ini
    transactions = Transaction.objects.filter(date__date=date)
    sales_total = transactions.aggregate(
        total=Coalesce(Sum('total'), 0, output_field=DecimalField())
    )['total']

    # Keuntungan dari penjualan
    profit_from_sales = TransactionItem.objects.filter(
        transaction__date__date=date
    ).aggregate(
        total=Coalesce(Sum('profit'), 0, output_field=DecimalField())
    )['total']

    # Modal dari penjualan
    cost_from_sales = TransactionItem.objects.filter(
        transaction__date__date=date
    ).aggregate(
        total=Coalesce(Sum('cost_price') * F('quantity'), 0, output_field=DecimalField())
    )['total']

    # Pengeluaran
    expenses = Expense.objects.filter(date=date).aggregate(
        total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
    )['total']

    # Pemasukan non-penjualan
    incomes = Income.objects.filter(date=date).aggregate(
        total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
    )['total']

    total_transactions = transactions.count()

    return {
        'date': date,
        'sales_total': sales_total,
        'cost_from_sales': cost_from_sales or 0,
        'profit_from_sales': profit_from_sales or 0,
        'expenses': expenses,
        'other_incomes': incomes,
        'net_income': (profit_from_sales or 0) + incomes - expenses,
        'total_transactions': total_transactions,
    }


def get_weekly_stats(start_date=None):
    """Mendapatkan statistik mingguan"""
    if start_date is None:
        today = timezone.now().date()
        start_date = today - timedelta(days=today.weekday())

    end_date = start_date + timedelta(days=6)

    profit_from_sales = TransactionItem.objects.filter(
        transaction__date__date__range=(start_date, end_date)
    ).aggregate(
        total=Coalesce(Sum('profit'), 0, output_field=DecimalField())
    )['total']

    sales_total = Transaction.objects.filter(
        date__date__range=(start_date, end_date)
    ).aggregate(
        total=Coalesce(Sum('total'), 0, output_field=DecimalField())
    )['total']

    expenses = Expense.objects.filter(
        date__range=(start_date, end_date)
    ).aggregate(
        total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
    )['total']

    incomes = Income.objects.filter(
        date__range=(start_date, end_date)
    ).aggregate(
        total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
    )['total']

    return {
        'start_date': start_date,
        'end_date': end_date,
        'sales_total': sales_total,
        'profit_from_sales': profit_from_sales or 0,
        'expenses': expenses,
        'other_incomes': incomes,
        'net_income': (profit_from_sales or 0) + incomes - expenses,
    }


def get_monthly_stats(year=None, month=None):
    """Mendapatkan statistik bulanan"""
    now = timezone.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month

    profit_from_sales = TransactionItem.objects.filter(
        transaction__date__year=year,
        transaction__date__month=month,
    ).aggregate(
        total=Coalesce(Sum('profit'), 0, output_field=DecimalField())
    )['total']

    sales_total = Transaction.objects.filter(
        date__year=year,
        date__month=month,
    ).aggregate(
        total=Coalesce(Sum('total'), 0, output_field=DecimalField())
    )['total']

    expenses = Expense.objects.filter(
        date__year=year,
        date__month=month,
    ).aggregate(
        total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
    )['total']

    incomes = Income.objects.filter(
        date__year=year,
        date__month=month,
    ).aggregate(
        total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
    )['total']

    return {
        'year': year,
        'month': month,
        'sales_total': sales_total,
        'profit_from_sales': profit_from_sales or 0,
        'expenses': expenses,
        'other_incomes': incomes,
        'net_income': (profit_from_sales or 0) + incomes - expenses,
    }