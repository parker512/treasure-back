# media/urls.py
from django.urls import path
from .views import PhotoUploadView

urlpatterns = [
    path('upload-photo/', PhotoUploadView.as_view(), name='upload_photo'),
]
