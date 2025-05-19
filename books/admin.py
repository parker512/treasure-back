from django.contrib import admin
from .models import Category, Genre, BookListing, Transaction

# Регистрируем модели
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(BookListing)

# Register Transaction model
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'buyer', 'seller', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('book__title', 'buyer__email', 'seller__email')
    readonly_fields = ('created_at', 'updated_at', 'paypal_transaction_id')
    date_hierarchy = 'created_at'