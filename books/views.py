from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied

from .models import BookListing, Category, Genre
from .serializers import BookListingSerializer, BookDetailSerializer, CategorySerializer, GenreSerializer, UserSerializer
from users.models import CustomUser
from rest_framework.generics import DestroyAPIView


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


class BookListingUpdateView(generics.RetrieveUpdateAPIView):
    queryset = BookListing.objects.all()
    serializer_class = BookListingSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def perform_update(self, serializer):
        book_listing = self.get_object()
        if book_listing.user != self.request.user:
            raise PermissionDenied("Вы не являетесь владельцем этого объявления.")
        serializer.save()


class BookListingListView(generics.ListAPIView):
    serializer_class = BookListingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BookListing.objects.filter(user=self.request.user)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreListView(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'items_per_page'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


class AllBookListingsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = BookListing.objects.select_related('user').all()

        # Поиск
        search_query = request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Город (по пользователю)
        city = request.query_params.get('city')
        if city:
            queryset = queryset.filter(user__region__iexact=city)

        # Наличие обложки
        has_photo = request.query_params.get('has_photo')
        if has_photo == 'true':
            queryset = queryset.exclude(photo=None)

        # Состояние книги
        condition = request.query_params.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)

        # Категория (тип обложки)
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name__iexact=category)

        genre_ids = request.query_params.get('genre_id')
        if genre_ids:
            id_list = [int(id.strip()) for id in genre_ids.split(',') if id.strip().isdigit()]
            if id_list:
                queryset = queryset.filter(genre__id__in=id_list)


        # Сортировка
        sort_param = request.query_params.get('sort')
        if sort_param == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_param == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_param == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_param == 'oldest':
            queryset = queryset.order_by('created_at')
        else:
            queryset = queryset.order_by('-created_at')


        # Пагинация и сериализация
        paginator = CustomPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)
        serializer = BookListingSerializer(paginated_qs, many=True)
        return paginator.get_paginated_response(serializer.data)


class BookDetailView(generics.RetrieveAPIView):
    queryset = BookListing.objects.all()
    serializer_class = BookDetailSerializer
    lookup_field = 'id'
    permission_classes = [AllowAny]


class UserBookListingsView(generics.ListAPIView):
    serializer_class = BookListingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return BookListing.objects.filter(user__id=user_id)

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
    

class BookListingDeleteView(DestroyAPIView):
    queryset = BookListing.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("Вы не можете удалить это объявление.")
        instance.delete()