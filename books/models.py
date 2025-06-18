from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class BookListing(models.Model):
    CONDITION_CHOICES = [
    ('new', 'Нова'),
    ('used', 'Б/У'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    author = models.CharField(max_length=255, default="Невідомий автор")

    photo = models.ForeignKey("media.Photo", on_delete=models.SET_NULL, null=True, related_name="listings")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="listings")
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, related_name="listings")
    created_at = models.DateTimeField(auto_now_add=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    is_sold = models.BooleanField(default=False) 

    @property
    def location(self):
        return self.user.region

    def __str__(self):
        return self.title
    
class Transaction(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Очікує оплати'),
        ('PAID', 'Оплачено'),
        ('SELLER_CONFIRMED', 'Продавець підтвердив відправку'),
        ('BUYER_CONFIRMED', 'Покупець підтвердив отримання'),
        ('COMPLETED', 'Завершено'),
        ('CANCELLED', 'Скасовано'),
        ('DISPUTED', 'Суперечка'),
    ]

    book = models.ForeignKey(BookListing, on_delete=models.CASCADE, related_name="transactions")
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="purchases")
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sales")
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount paid
    platform_commission = models.DecimalField(max_digits=10, decimal_places=2)  # Commission taken
    seller_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount to seller
    paypal_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    seller_confirmation_deadline = models.DateTimeField(null=True, blank=True)
    buyer_confirmation_deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Transaction {self.id} for {self.book.title}"
    
class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    book_listing = models.ForeignKey(BookListing, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book_listing')  # Один пользователь не может добавить одно объявление дважды

    def __str__(self):
        return f"{self.user.email} favorited {self.book_listing.title}"