from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import BookListing, Category, Genre
from .serializers import BookListingSerializer, CategorySerializer, GenreSerializer
from rest_framework import generics
from .models import BookListing
from .serializers import BookDetailSerializer, BookListingSerializer
from users.serializers import UserSerializer
from users.models import CustomUser
from rest_framework.response import Response
from rest_framework import status


class BookListingCreateView(generics.CreateAPIView):
    serializer_class = BookListingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookListingListView(generics.ListAPIView):
    serializer_class = BookListingSerializer
    permission_classes = [IsAuthenticated]  # Ограничиваем доступ

    def get_queryset(self):
        # Показываем только объявления текущего пользователя
        return BookListing.objects.filter(user=self.request.user)

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class GenreListView(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

class AllBookListingsView(generics.ListAPIView):
    serializer_class = BookListingSerializer
    permission_classes = [AllowAny]  # Доступно всем, даже неавторизованным (можно изменить на IsAuthenticated)

    def get_queryset(self):
        # Возвращаем все объявления
        return BookListing.objects.all()
    
# Получить одно объявление + пользователя
class BookDetailView(generics.RetrieveAPIView):
    queryset = BookListing.objects.all()
    serializer_class = BookDetailSerializer
    lookup_field = 'id'  # По id обьявления
    permission_classes = [AllowAny]

# Получить все объявления пользователя
class UserBookListingsView(generics.ListAPIView):
    serializer_class = BookListingSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return BookListing.objects.filter(user_id=user_id)

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        listings = self.get_queryset()
        user_data = UserSerializer(user).data
        listings_data = BookListingSerializer(listings, many=True).data

        return Response({
            "user": user_data,
            "listings": listings_data
        })