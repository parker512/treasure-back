from rest_framework.parsers import MultiPartParser, FormParser  # Добавляем MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Photo

class PhotoUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)  # Используем MultiPartParser и FormParser

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')  # Ожидаем ключ 'file'
        if file:
            photo = Photo.objects.create(image=file)
            return Response({'id': photo.id, 'image_path': photo.image.url}, status=status.HTTP_201_CREATED)
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)