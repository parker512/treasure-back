from django.urls import path
from .views import BookListingCreateView, BookListingListView, CategoryListView, GenreListView,  AllBookListingsView, BookDetailView, UserBookListingsView, BookListingUpdateView,BookListingDeleteView

urlpatterns = [
    path('create/', BookListingCreateView.as_view(), name='book-listing-create'),
    path('list/', BookListingListView.as_view(), name='book-listing-list'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('genres/', GenreListView.as_view(), name='genre-list'),
    path('book-listings/all/', AllBookListingsView.as_view(), name='all_book_listings'),
        path('book/<int:id>/', BookDetailView.as_view(), name='book-detail'),  # новое
    path('user/<int:user_id>/listings/', UserBookListingsView.as_view(), name='user-book-listings'), 
    path('book/<int:id>/update/', BookListingUpdateView.as_view(), name='book-update'),
    path('book/<int:id>/delete/', BookListingDeleteView.as_view(), name='book-delete'),

]