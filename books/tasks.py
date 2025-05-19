# books/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Transaction

@shared_task
def auto_complete_transactions():
    transactions = Transaction.objects.filter(
        status='SELLER_CONFIRMED',
        buyer_confirmation_deadline__lte=timezone.now()
    )
    for transaction in transactions:
        transaction.status = 'COMPLETED'
        transaction.save()