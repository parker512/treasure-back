from rest_framework import serializers
from .models import BookListing, Category, Genre
from media.models import Photo  # Импортируем модель Photo
from users.serializers import UserSerializer

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

class BookListingSerializer(serializers.ModelSerializer):
    # Поле photo ожидает ID при создании, но отображает данные Photo
    photo = serializers.PrimaryKeyRelatedField(queryset=Photo.objects.all(), write_only=True)
    photo_detail = PhotoSerializer(source='photo', read_only=True)  # Для отображения деталей фото
    condition = serializers.ChoiceField(choices=BookListing.CONDITION_CHOICES)

    # Поля category и genre отображаем с деталями
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    genre = GenreSerializer(read_only=True)
    genre_id = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), source='genre', write_only=True
    )

    # Поле user отображаем как ID, но только для чтения
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = BookListing
        fields = [
            'id', 'title', 'description', 'price', 'photo', 'photo_detail',
            'category', 'category_id', 'genre', 'genre_id', 'user',
            'created_at', 'location', 'condition'
        ]
        read_only_fields = ['user', 'created_at', 'location']


class BookDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    photo_detail = PhotoSerializer(source='photo', read_only=True)
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True)

    # Добавь это, если хочешь показывать "Нова" / "Б/У", а не "new" / "used"
    condition = serializers.CharField(source='get_condition_display', read_only=True)

    class Meta:
        model = BookListing
        fields = [
            'id', 'title', 'description', 'price', 'photo_detail',
            'category', 'genre', 'user', 'created_at',
            'condition', 'location'  # <-- добавлены
        ]
