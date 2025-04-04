from django import forms
from .models import BookListing

class BookListingForm(forms.ModelForm):
    class Meta:
        model = BookListing
        fields = ['title', 'description', 'price', 'category', 'genre']

    def save(self, commit=True):
        # Связываем пользователя с объявлением
        book_listing = super().save(commit=False)
        if commit:
            book_listing.user = self.request.user  # Привязываем к текущему пользователю
            book_listing.save()
        return book_listing
