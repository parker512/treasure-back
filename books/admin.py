from django.contrib import admin
from .models import Category, Genre, BookListing

# Регистрируем модели
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(BookListing)
