from rest_framework.response import Response
from rest_framework import viewsets
from books.serializers import BookSerializer
from characters.models import Character
from characters.serializers import CharacterSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import OAuth2Authentication


class CharacterViewSet(viewsets.ModelViewSet):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    # authentication_classes = [OAuth2Authentication]
    # permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        character = self.get_object()
        books = character.books.all()
        serializer = BookSerializer(books, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def pov_books(self, request, pk=None):
        character = self.get_object()
        books = character.pov_books.all()
        serializer = BookSerializer(books, many=True, context={'request': request})
        return Response(serializer.data)
