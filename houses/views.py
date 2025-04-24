from rest_framework import viewsets
from houses.models import House
from houses.serializers import HouseSerializer

class HouseViewSet(viewsets.ModelViewSet):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
