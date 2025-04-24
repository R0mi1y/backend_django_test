from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from books.views import BookViewSet
from characters.views import CharacterViewSet
from houses.views import HouseViewSet

router = DefaultRouter()

router.register(r'books', BookViewSet)
router.register(r'characters', CharacterViewSet)
router.register(r'houses', HouseViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]
