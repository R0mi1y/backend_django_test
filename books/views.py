from itertools import chain
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from books.models import Book
from books.serializers import BookSerializer
import base64
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from characters.serializers import CharacterSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    authentication_classes = [OAuth2Authentication]
    
    @action(detail=False, methods=['get'])
    def all_pov_characters(self, request, pk=None):
        books = Book.objects.prefetch_related('pov_characters')
        all_pov_chars = set(chain.from_iterable(book.pov_characters.all() for book in books))
        serializer = CharacterSerializer(all_pov_chars, many=True, context={'request': request})
        return Response(serializer.data)
    
    
    @action(detail=True, methods=['get'])
    def pov_characters(self, request, pk=None):
        book = self.get_object()
        
        pov_characters = book.pov_characters.all()
        serializer = CharacterSerializer(pov_characters, many=True, context={'request': request})
        return Response(serializer.data)
    
    
    @action(detail=True, methods=['get'])
    def characters(self, request, pk=None):
        book = self.get_object()
        
        characters = book.characters.all()
        serializer = CharacterSerializer(characters, many=True, context={'request': request})
        return Response(serializer.data)
    
    
    # @action(detail=True, methods=['get'])
    # def cover(self, request, pk=None):
    #     book = self.get_object()
        
    #     if not book.cover_base64:
    #         return Response({'error': 'No cover image available'}, status=404)
        
    #     try:
    #         image_data = base64.b64decode(book.cover_base64)
    #         return HttpResponse(image_data, content_type='image/jpeg')
    #     except:
    #         return Response({'error': 'Invalid image data'}, status=400)
    
    
    @action(detail=True, methods=['get'])
    def cover(self, request, pk=None):
        book = self.get_object()
        
        if not book.cover_base64:
            return Response({'error': 'No cover image available'}, status=404)
        
        try:
            image_data = base64.b64decode(book.cover_base64)
            image = Image.open(BytesIO(image_data))
            
            # Criar uma nova camada para o fundo semi transparente
            overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            try:
                title_font = ImageFont.truetype("arial.ttf", 30)
                chars_font = ImageFont.truetype("arial.ttf", 20)
            except:
                title_font = ImageFont.load_default()
                chars_font = ImageFont.load_default()
            
            title_position = (10, 50)
            pov_chars_position = (30, 100)
            
            pov_chars = "".join(i.name + "\n" for i in book.pov_characters.all())
            
            # Calcular o tamanho do texto para criar o retângulo de fundo
            title_bbox = draw.textbbox(title_position, book.name, font=title_font)
            pov_chars_bbox = draw.textbbox(pov_chars_position, pov_chars, font=chars_font)
            
            draw.rounded_rectangle([title_bbox[0]-5, title_bbox[1]-5, title_bbox[2]+5, title_bbox[3]+5],
                        radius=10,
                        fill=(0, 0, 0, 64))
            draw.rounded_rectangle([pov_chars_bbox[0]-5, pov_chars_bbox[1]-5, pov_chars_bbox[2]+5, pov_chars_bbox[3]+5], 
                        radius=10,
                        fill=(0, 0, 0, 64))
            
            draw.text(title_position, book.name, font=title_font, fill=(255, 255, 255, 170))
            draw.text(pov_chars_position, pov_chars, font=chars_font, fill=(255, 255, 255, 170))
            
            # Combinar a imagem original com a camada de overlay
            image = Image.alpha_composite(image.convert('RGBA'), overlay)
            
            image = image.convert('RGB')
            
            buffer = BytesIO()
            image.save(buffer, format='JPEG')
            buffer.seek(0)
            
            return HttpResponse(buffer, content_type='image/jpeg')
        except Exception as e:
            return Response({'error': f'Error processing image: {str(e)}'}, status=400)
