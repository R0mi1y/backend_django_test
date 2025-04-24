from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from books.models import Book
from books.serializers import BookSerializer
import base64

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @action(detail=True, methods=['get'])
    def cover(self, request, pk=None):
        book = self.get_object()
        
        if not book.cover_base64:
            return Response({'error': 'No cover image available'}, status=404)
        
        try:
            image_data = base64.b64decode(book.cover_base64)
            return HttpResponse(image_data, content_type='image/jpeg')
        except:
            return Response({'error': 'Invalid image data'}, status=400)
