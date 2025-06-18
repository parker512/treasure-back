# books/views.py
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import paypalrestsdk
from .models import BookListing, Transaction, Category, Genre
from .serializers import BookListingSerializer, BookDetailSerializer, CategorySerializer, GenreSerializer, TransactionSerializer
from .utils import configure_paypal
from django.conf import settings
from users.models import CustomUser
from users.serializers import UserSerializer
from .models import Favorite
from .serializers import FavoriteSerializer


# Existing views (unchanged)
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

        search_query = request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        city = request.query_params.get('city')
        if city:
            queryset = queryset.filter(user__region__iexact=city)

        has_photo = request.query_params.get('has_photo')
        if has_photo == 'true':
            queryset = queryset.exclude(photo=None)

        condition = request.query_params.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)

        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name__iexact=category)

        genre_ids = request.query_params.get('genre_id')
        if genre_ids:
            id_list = [int(id.strip()) for id in genre_ids.split(',') if id.strip().isdigit()]
            if id_list:
                queryset = queryset.filter(genre__id__in=id_list)

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

class BookListingDeleteView(generics.DestroyAPIView):
    queryset = BookListing.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("Вы не можете удалить это объявление.")
        instance.delete()


# books/views.py
# ... other imports ...
# books/views.py
# ... other imports ...

class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id):
        try:
            book = BookListing.objects.get(id=book_id)
        except BookListing.DoesNotExist:
            return Response({"error": "Книга не найдена"}, status=status.HTTP_404_NOT_FOUND)

        if book.is_sold:
            return Response({"error": "Книга уже продана"}, status=status.HTTP_400_BAD_REQUEST)

        if book.user == request.user:
            return Response({"error": "Вы не можете купить собственную книгу"}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate amounts
        amount = book.price
        commission = (Decimal(settings.PLATFORM_COMMISSION_PERCENT) / 100) * amount
        seller_amount = amount - commission

        # Create transaction
        transaction = Transaction.objects.create(
            book=book,
            buyer=request.user,
            seller=book.user,
            amount=amount,
            platform_commission=commission,
            seller_amount=seller_amount,
            status='PENDING',
            seller_confirmation_deadline=timezone.now() + timedelta(hours=settings.SELLER_CONFIRMATION_HOURS)
        )

        # Configure PayPal
        configure_paypal()

        # Create PayPal payment
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": str(amount),
                    "currency": "USD"  # Adjust currency as needed
                },
                "description": f"Покупка книги: {book.title}"
            }],
            "redirect_urls": {
                "return_url": "http://localhost:5173/book/" + str(book_id),  # Redirect to frontend
                "cancel_url": "http://localhost:5173/book/" + str(book_id) + "?cancelled=true"
            }
        })

        if payment.create():
            transaction.paypal_transaction_id = payment.id
            transaction.save()
            for link in payment.links:
                if link.rel == "approval_url":
                    return Response({"approval_url": link.href, "transaction_id": transaction.id}, status=status.HTTP_200_OK)
        else:
            transaction.delete()
            return Response({"error": payment.error}, status=status.HTTP_400_BAD_REQUEST)

class ExecutePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payment_id = request.query_params.get('paymentId')
        payer_id = request.query_params.get('PayerID')

        if not payment_id or not payer_id:
            return Response({"error": "Недостаточно данных для выполнения платежа"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            transaction = Transaction.objects.get(paypal_transaction_id=payment_id)
        except Transaction.DoesNotExist:
            return Response({"error": "Транзакция не найдена"}, status=status.HTTP_404_NOT_FOUND)

        if transaction.buyer != request.user:
            return Response({"error": "Недостаточно прав"}, status=status.HTTP_403_FORBIDDEN)

        configure_paypal()
        payment = paypalrestsdk.Payment.find(payment_id)

        if payment.execute({"payer_id": payer_id}):
            transaction.status = 'PAID'
            transaction.book.is_sold = True
            transaction.save()
            transaction.book.save()
            return Response({"message": "Платеж успешно выполнен", "transaction_id": transaction.id}, status=status.HTTP_200_OK)
        else:
            transaction.status = 'CANCELLED'
            transaction.save()
            return Response({"error": payment.error}, status=status.HTTP_400_BAD_REQUEST)

class CancelPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payment_id = request.query_params.get('paymentId')
        try:
            transaction = Transaction.objects.get(paypal_transaction_id=payment_id)
        except Transaction.DoesNotExist:
            return Response({"error": "Транзакция не найдена"}, status=status.HTTP_404_NOT_FOUND)

        if transaction.buyer != request.user:
            return Response({"error": "Недостаточно прав"}, status=status.HTTP_403_FORBIDDEN)

        transaction.status = 'CANCELLED'
        transaction.save()
        return Response({"message": "Платеж отменен"}, status=status.HTTP_200_OK)

class SellerConfirmShipmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, transaction_id):
        try:
            transaction = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            return Response({"error": "Транзакция не найдена"}, status=status.HTTP_404_NOT_FOUND)

        if transaction.seller != request.user:
            return Response({"error": "Вы не продавец этой книги"}, status=status.HTTP_403_FORBIDDEN)

        if transaction.status != 'PAID':
            return Response({"error": "Транзакция не в статусе 'Оплачено'"}, status=status.HTTP_400_BAD_REQUEST)

        if timezone.now() > transaction.seller_confirmation_deadline:
            # Auto-cancel and refund
            configure_paypal()
            try:
                sale = paypalrestsdk.Sale.find(transaction.paypal_transaction_id)
                refund = sale.refund({"amount": {"total": str(transaction.amount), "currency": "USD"}})
                if refund.success():
                    transaction.status = 'CANCELLED'
                    transaction.book.is_sold = False
                    transaction.save()
                    transaction.book.save()
                    return Response({"error": "Срок подтверждения истек, транзакция отменена"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": refund.error}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        transaction.status = 'SELLER_CONFIRMED'
        transaction.buyer_confirmation_deadline = timezone.now() + timedelta(days=settings.BUYER_CONFIRMATION_DAYS)
        transaction.save()
        return Response({"message": "Отправка подтверждена"}, status=status.HTTP_200_OK)

class BuyerConfirmReceiptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, transaction_id):
        try:
            transaction = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            return Response({"error": "Транзакция не найдена"}, status=status.HTTP_404_NOT_FOUND)

        if transaction.buyer != request.user:
            return Response({"error": "Вы не покупатель этой книги"}, status=status.HTTP_403_FORBIDDEN)

        if transaction.status != 'SELLER_CONFIRMED':
            return Response({"error": "Продавец еще не подтвердил отправку"}, status=status.HTTP_400_BAD_REQUEST)

        transaction.status = 'BUYER_CONFIRMED'
        transaction.save()
        # Auto-complete after buyer confirmation
        transaction.status = 'COMPLETED'
        transaction.save()
        return Response({"message": "Получение подтверждено, сделка завершена"}, status=status.HTTP_200_OK)

class SellerTransactionsView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(seller=self.request.user).select_related('book', 'buyer', 'seller')

class BuyerTransactionsView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(buyer=self.request.user).select_related('book', 'buyer', 'seller')

class BuyerDisputeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, transaction_id):
        try:
            transaction = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            return Response({"error": "Транзакция не найдена"}, status=status.HTTP_404_NOT_FOUND)

        if transaction.buyer != request.user:
            return Response({"error": "Вы не покупатель этой книги"}, status=status.HTTP_403_FORBIDDEN)

        if transaction.status != 'SELLER_CONFIRMED':
            return Response({"error": "Продавец еще не подтвердил отправку"}, status=status.HTTP_400_BAD_REQUEST)

        if timezone.now() > transaction.buyer_confirmation_deadline:
            # Auto-complete if deadline passed
            transaction.status = 'COMPLETED'
            transaction.save()
            return Response({"error": "Срок подтверждения истек, сделка завершена"}, status=status.HTTP_400_BAD_REQUEST)

        transaction.status = 'DISPUTED'
        transaction.save()
        return Response({"message": "Суперечка открыта, ожидайте решения администратора"}, status=status.HTTP_200_OK)
    
class FavoriteListCreateView(generics.ListCreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FavoriteDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, book_listing_id):
        try:
            favorite = Favorite.objects.get(
                user=request.user, book_listing_id=book_listing_id
            )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response(
                {"detail": "Объявление не найдено в избранном"},
                status=status.HTTP_404_NOT_FOUND
            )