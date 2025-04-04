from django.contrib import admin  # Добавь этот импорт
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/books/', include('books.urls')),  # Подключаем маршруты для книг
     path('api/media/', include('media.urls')),
]
