from rest_framework import viewsets
from houses.models import House
from houses.serializers import HouseSerializer
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import OAuth2Authentication

class HouseViewSet(viewsets.ModelViewSet):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    # authentication_classes = [OAuth2Authentication]
    # permission_classes = [IsAuthenticated]
