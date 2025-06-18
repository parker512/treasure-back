# books/urls.py
from django.urls import path
from .views import (
    BookListingCreateView, BookListingListView, CategoryListView, GenreListView,
    AllBookListingsView, BookDetailView, UserBookListingsView, BookListingUpdateView,
    BookListingDeleteView, InitiatePaymentView, ExecutePaymentView, CancelPaymentView,
    SellerConfirmShipmentView, BuyerConfirmReceiptView, BuyerDisputeView, SellerTransactionsView, BuyerTransactionsView, FavoriteListCreateView, FavoriteDeleteView
)

urlpatterns = [
    path('create/', BookListingCreateView.as_view(), name='book-listing-create'),
    path('list/', BookListingListView.as_view(), name='book-listing-list'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('genres/', GenreListView.as_view(), name='genre-list'),
    path('book-listings/all/', AllBookListingsView.as_view(), name='all_book_listings'),
    path('book/<int:id>/', BookDetailView.as_view(), name='book-detail'),
    path('user/<int:user_id>/listings/', UserBookListingsView.as_view(), name='user-book-listings'),
    path('book/<int:id>/update/', BookListingUpdateView.as_view(), name='book-update'),
    path('book/<int:id>/delete/', BookListingDeleteView.as_view(), name='book-delete'),
    path('book/<int:book_id>/payment/initiate/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('payment/execute/', ExecutePaymentView.as_view(), name='execute-payment'),
    path('payment/cancel/', CancelPaymentView.as_view(), name='cancel-payment'),
    path('transaction/<int:transaction_id>/seller-confirm/', SellerConfirmShipmentView.as_view(), name='seller-confirm'),
    path('transaction/<int:transaction_id>/buyer-confirm/', BuyerConfirmReceiptView.as_view(), name='buyer-confirm'),
    path('transaction/<int:transaction_id>/dispute/', BuyerDisputeView.as_view(), name='buyer-dispute'),
    path('seller/transactions/', SellerTransactionsView.as_view(), name='seller-transactions'),
    path('buyer/transactions/', BuyerTransactionsView.as_view(), name='buyer-transactions'),
    path('favorites/', FavoriteListCreateView.as_view(), name='favorite-list-create'),
    path('favorites/<int:book_listing_id>/', FavoriteDeleteView.as_view(), name='favorite-delete'),
]