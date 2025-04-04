from django.urls import path
from .views import BookListingCreateView, BookListingListView, CategoryListView, GenreListView

urlpatterns = [
    path('create/', BookListingCreateView.as_view(), name='book-listing-create'),
    path('list/', BookListingListView.as_view(), name='book-listing-list'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('genres/', GenreListView.as_view(), name='genre-list'),
]