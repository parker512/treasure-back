from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class BookListing(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.ForeignKey("media.Photo", on_delete=models.SET_NULL, null=True, related_name="listings")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="listings")
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, related_name="listings")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def location(self):
        return self.user.city

    def __str__(self):
        return self.title