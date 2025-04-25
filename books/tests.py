import base64
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from oauth2_provider.models import Application, AccessToken
import pytz
from .models import Book
from characters.models import Character


class BookModelTest(TestCase):
    """Testes para o modelo Book"""
    
    def setUp(self):
        self.book_data = {
            'external_id': 1,
            'name': 'A Game of Thrones',
            'isbn': '978-0553103540',
            'authors': ['George R. R. Martin'],
            'number_of_pages': 694,
            'publisher': 'Bantam Books',
            'country': 'United States',
            'media_type': 'Hardcover',
            'released': datetime(1996, 8, 1, 0, 0, tzinfo=pytz.UTC),
            'cover_base64': 'VGVzdGUgZGUgaW1hZ2Vt'  # "Teste de imagem" em base64
        }
        self.book = Book.objects.create(**self.book_data)
        
        # Criar personagem para testar relacionamentos
        self.character = Character.objects.create(
            external_id=1,
            name='Jon Snow',
            gender='Male',
            culture='Northmen'
        )
        
        # Adicionar personagem ao livro
        self.book.characters.add(self.character)
        self.book.pov_characters.add(self.character)
    
    def test_book_creation(self):
        """Teste de criação do livro"""
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(self.book.name, 'A Game of Thrones')
        self.assertEqual(self.book.external_id, 1)
        self.assertEqual(self.book.isbn, '978-0553103540')
        self.assertEqual(self.book.number_of_pages, 694)
        
    def test_book_characters_relation(self):
        """Teste de relacionamento entre livro e personagens"""
        self.assertEqual(self.book.characters.count(), 1)
        self.assertEqual(self.book.pov_characters.count(), 1)
        self.assertEqual(self.book.characters.first().name, 'Jon Snow')
        
    def test_book_str_method(self):
        """Teste do método __str__ do modelo Book"""
        self.assertEqual(str(self.book), 'A Game of Thrones')


class BookAPITest(APITestCase):
    """Testes para a API de Books"""
    
    def setUp(self):
        self.client = APIClient()
        self.book_data = {
            'external_id': 1,
            'name': 'A Game of Thrones',
            'isbn': '978-0553103540',
            'authors': ['George R. R. Martin'],
            'number_of_pages': 694,
            'publisher': 'Bantam Books',
            'country': 'United States',
            'media_type': 'Hardcover',
            'released': '1996-08-01T00:00:00Z',
            'cover_base64': 'VGVzdGUgZGUgaW1hZ2Vt'  # "Teste de imagem" em base64
        }
        
        # Criar um livro para teste
        self.book = Book.objects.create(
            external_id=1,
            name='A Game of Thrones',
            isbn='978-0553103540',
            authors=['George R. R. Martin'],
            number_of_pages=694,
            publisher='Bantam Books',
            country='United States',
            media_type='Hardcover',
            released=datetime(1996, 8, 1, 0, 0, tzinfo=pytz.UTC),
            cover_base64='VGVzdGUgZGUgaW1hZ2Vt'
        )
        
        # Criar usuário e token para autenticação
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpassword'
        )
        
        # Criar aplicação OAuth2
        self.application = Application.objects.create(
            name='Test Application',
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
            user=self.user
        )
        
        # Criar token de acesso
        self.access_token = AccessToken.objects.create(
            user=self.user,
            application=self.application,
            token='test-token',
            expires=timezone.now() + timezone.timedelta(days=1),
            scope='read write'
        )
        
        # Autenticar o cliente
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token.token}')
        
        # URLs para testes
        self.list_url = reverse('book-list')
        self.detail_url = reverse('book-detail', args=[self.book.id])
        self.cover_url = reverse('book-cover', args=[self.book.id])
    
    def test_get_book_list(self):
        """Teste para obter lista de livros"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # A resposta pode ser paginada ou não
        if isinstance(response.data, dict) and 'results' in response.data:
            # Resposta paginada
            self.assertGreaterEqual(len(response.data['results']), 1)
        else:
            # Resposta não paginada
            self.assertGreaterEqual(len(response.data), 1)
        
    def test_get_book_detail(self):
        """Teste para obter detalhe de um livro"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'A Game of Thrones')
        self.assertEqual(response.data['external_id'], 1)
        
    def test_get_book_cover(self):
        """Teste para obter capa de um livro"""
        response = self.client.get(self.cover_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # O content_type deve ser 'image/jpeg'
        self.assertEqual(response['Content-Type'], 'image/jpeg')
        
    def test_get_nonexistent_book_cover(self):
        """Teste para obter capa de um livro sem capa"""
        # Criar livro sem capa
        book_no_cover = Book.objects.create(
            external_id=2,
            name='Livro Sem Capa',
            isbn='000-0000000000',
            authors=['Autor Teste'],
            number_of_pages=100,
            publisher='Editora Teste',
            country='Brasil',
            media_type='Hardcover',
            released=datetime(2020, 1, 1, 0, 0, tzinfo=pytz.UTC),
            cover_base64=None
        )
        cover_url = reverse('book-cover', args=[book_no_cover.id])
        
        response = self.client.get(cover_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
