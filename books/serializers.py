from rest_framework import serializers
from .models import BookListing, Category, Genre, Transaction
from media.models import Photo  # Импортируем модель Photo
from users.serializers import UserSerializer
from .models import Favorite

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']  # Явно указываем поля

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']  # Явно указываем поля

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'image']  # Для отображения URL фото


class BookTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookListing
        fields = ['id', 'title']

class TransactionSerializer(serializers.ModelSerializer):
    book = BookTransactionSerializer(read_only=True)
    buyer = UserSerializer(read_only=True)
    seller = UserSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'book', 'buyer', 'seller', 'amount', 'platform_commission',
            'seller_amount', 'paypal_transaction_id', 'status', 'created_at',
            'updated_at', 'seller_confirmation_deadline', 'buyer_confirmation_deadline'
        ]

class BookDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    photo_detail = PhotoSerializer(source='photo', read_only=True)
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True)
    condition = serializers.CharField(source='get_condition_display', read_only=True)
    transactions = TransactionSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = BookListing
        fields = [
            'id', 'title', 'description', 'price', 'photo_detail',
            'category', 'genre', 'user', 'created_at',
            'condition', 'location', 'is_sold', 'transactions', 'is_favorited'
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, book_listing=obj).exists()
        return False

class BookListingSerializer(serializers.ModelSerializer):
    photo = serializers.PrimaryKeyRelatedField(queryset=Photo.objects.all(), write_only=True)
    photo_detail = PhotoSerializer(source='photo', read_only=True)
    condition = serializers.ChoiceField(choices=BookListing.CONDITION_CHOICES)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    genre = GenreSerializer(read_only=True)
    genre_id = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), source='genre', write_only=True
    )
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    transactions = TransactionSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = BookListing
        fields = [
            'id', 'title', 'description', 'price', 'photo', 'photo_detail',
            'category', 'category_id', 'genre', 'genre_id', 'user',
            'created_at', 'location', 'condition', 'is_sold', 'transactions', 'is_favorited'
        ]
        read_only_fields = ['user', 'created_at', 'location', 'is_sold', 'transactions']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, book_listing=obj).exists()
        return False
    
class FavoriteSerializer(serializers.ModelSerializer):
    book_listing = BookListingSerializer(read_only=True)
    book_listing_id = serializers.PrimaryKeyRelatedField(
        queryset=BookListing.objects.all(), source='book_listing', write_only=True
    )

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'book_listing', 'book_listing_id', 'created_at']
        read_only_fields = ['user', 'created_at']