from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from books.views import BookViewSet
from characters.views import CharacterViewSet
from houses.views import HouseViewSet
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="API de Game of Thrones",
      default_version='v1',
      description="API para consulta de informações sobre Game of Thrones",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()

router.register(r'books', BookViewSet)
router.register(r'characters', CharacterViewSet)
router.register(r'houses', HouseViewSet)

urlpatterns = [
   path('admin/', admin.site.urls),
   path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
   path('api/', include(router.urls)),
   path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
