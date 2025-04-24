from rest_framework import serializers
from characters.models import Character

class CharacterSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='character-detail',
        lookup_field='pk'
    )
    father = serializers.HyperlinkedRelatedField(
        view_name='character-detail',
        read_only=True
    )
    mother = serializers.HyperlinkedRelatedField(
        view_name='character-detail',
        read_only=True
    )
    spouse = serializers.HyperlinkedRelatedField(
        view_name='character-detail',
        read_only=True
    )
    allegiances = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='house-detail',
        read_only=True
    )
    books = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='book-detail',
        read_only=True
    )
    pov_books = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='book-detail',
        read_only=True
    )

    class Meta:
        model = Character
        fields = [
            'url', 'external_id', 'name', 'gender', 'culture',
            'born', 'died', 'titles', 'aliases', 'father',
            'mother', 'spouse', 'allegiances', 'books',
            'pov_books', 'tv_series', 'played_by'
        ]