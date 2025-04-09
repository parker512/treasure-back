from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import BookListing, Category, Genre
from .serializers import BookListingSerializer, CategorySerializer, GenreSerializer

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