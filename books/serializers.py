from rest_framework import serializers
from books.models import Book
from characters.models import Character

class BookSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='book-detail',
        lookup_field='pk'
    )
    cover_url = serializers.HyperlinkedIdentityField(
        view_name='book-cover',
        lookup_field='pk'
    )
    characters = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='character-detail',
        read_only=True
    )
    pov_characters = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='character-detail',
        read_only=True
    )

    class Meta:
        model = Book
        fields = [
            'url', 'external_id', 'name', 'isbn', 'authors',
            'number_of_pages', 'publisher', 'country', 'media_type',
            'released', 'cover_base64', 'cover_url', 'characters',
            'pov_characters'
        ]
