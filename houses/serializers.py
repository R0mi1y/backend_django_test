from rest_framework import serializers
from houses.models import House

class HouseSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='house-detail',
        lookup_field='pk'
    )
    current_lord = serializers.HyperlinkedRelatedField(
        view_name='character-detail',
        read_only=True
    )
    heir = serializers.HyperlinkedRelatedField(
        view_name='character-detail',
        read_only=True
    )
    overlord = serializers.HyperlinkedRelatedField(
        view_name='house-detail',
        read_only=True
    )
    founder = serializers.HyperlinkedRelatedField(
        view_name='character-detail',
        read_only=True
    )
    cadet_branches = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='house-detail',
        read_only=True
    )
    sworn_members = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='character-detail',
        read_only=True
    )

    class Meta:
        model = House
        fields = [
            'url', 'external_id', 'name', 'region', 'coat_of_arms',
            'words', 'titles', 'seats', 'founded', 'died_out',
            'ancestral_weapons', 'current_lord', 'heir', 'overlord',
            'founder', 'cadet_branches', 'sworn_members'
        ]