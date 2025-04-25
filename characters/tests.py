from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from oauth2_provider.models import Application, AccessToken
import pytz
from .models import Character
from books.models import Book
from houses.models import House


class CharacterModelTest(TestCase):
    """Testes para o modelo Character"""
    
    def setUp(self):
        # Criar personagem principal
        self.character_data = {
            'external_id': 583,
            'name': 'Jon Snow',
            'gender': 'Male',
            'culture': 'Northmen',
            'born': 'In 283 AC',
            'died': '',
            'titles': ['Lord Commander of the Night\'s Watch'],
            'aliases': ['Lord Snow', 'The Bastard of Winterfell'],
        }
        self.character = Character.objects.create(**self.character_data)
        
        # Criar personagem para ser pai
        self.father = Character.objects.create(
            external_id=339,
            name='Eddard Stark',
            gender='Male',
            culture='Northmen'
        )
        
        # Criar personagem para ser mãe (não revelada no livro, apenas para testes)
        self.mother = Character.objects.create(
            external_id=100,
            name='Unknown Mother',
            gender='Female'
        )
        
        # Criar livro para testar relacionamentos
        self.book = Book.objects.create(
            external_id=1,
            name='A Game of Thrones',
            isbn='978-0553103540',
            authors=['George R. R. Martin'],
            number_of_pages=694,
            publisher='Bantam Books',
            country='United States',
            media_type='Hardcover',
            released=datetime(1996, 8, 1, 0, 0, tzinfo=pytz.UTC)
        )
        
        # Criar casa para testar relacionamentos
        self.house = House.objects.create(
            external_id=362,
            name='House Stark of Winterfell',
            region='The North',
            words='Winter is Coming'
        )
        
        # Estabelecer relações
        self.character.father = self.father
        self.character.mother = self.mother
        self.character.save()
        
        self.character.books.add(self.book)
        self.character.pov_books.add(self.book)
        self.character.allegiances.add(self.house)
    
    def test_character_creation(self):
        """Teste de criação do personagem"""
        self.assertEqual(Character.objects.count(), 3)  # 3 personagens criados no setup
        self.assertEqual(self.character.name, 'Jon Snow')
        self.assertEqual(self.character.external_id, 583)
        self.assertEqual(self.character.gender, 'Male')
        self.assertEqual(self.character.culture, 'Northmen')
        
    def test_character_relations(self):
        """Teste de relacionamentos do personagem"""
        self.assertEqual(self.character.father.name, 'Eddard Stark')
        self.assertEqual(self.character.mother.name, 'Unknown Mother')
        self.assertEqual(self.character.books.count(), 1)
        self.assertEqual(self.character.pov_books.count(), 1)
        self.assertEqual(self.character.allegiances.count(), 1)
        self.assertEqual(self.character.allegiances.first().name, 'House Stark of Winterfell')
        
    def test_character_array_fields(self):
        """Teste dos campos JSON do personagem"""
        self.assertEqual(len(self.character.titles), 1)
        self.assertEqual(len(self.character.aliases), 2)
        self.assertIn('Lord Snow', self.character.aliases)
        
    def test_character_str_method(self):
        """Teste do método __str__ do modelo Character"""
        self.assertEqual(str(self.character), 'Jon Snow')
        
        # Teste para personagem sem nome (usando apenas external_id)
        nameless_char = Character.objects.create(
            external_id=999,
            gender='Unknown'
        )
        self.assertEqual(str(nameless_char), 'Character 999')


class CharacterAPITest(APITestCase):
    """Testes para a API de Characters"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Criar personagem para teste
        self.character = Character.objects.create(
            external_id=583,
            name='Jon Snow',
            gender='Male',
            culture='Northmen',
            born='In 283 AC',
            died='',
            titles=['Lord Commander of the Night\'s Watch'],
            aliases=['Lord Snow', 'The Bastard of Winterfell']
        )
        
        # Criar livro para teste de relacionamento
        self.book = Book.objects.create(
            external_id=1,
            name='A Game of Thrones',
            isbn='978-0553103540',
            authors=['George R. R. Martin'],
            number_of_pages=694,
            publisher='Bantam Books',
            country='United States',
            media_type='Hardcover',
            released=datetime(1996, 8, 1, 0, 0, tzinfo=pytz.UTC)
        )
        
        # Relacionar livro e personagem
        self.character.books.add(self.book)
        
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
        self.list_url = reverse('character-list')
        self.detail_url = reverse('character-detail', args=[self.character.id])
    
    def test_get_character_list(self):
        """Teste para obter lista de personagens"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # A resposta pode ser paginada ou não
        if isinstance(response.data, dict) and 'results' in response.data:
            # Resposta paginada
            self.assertGreaterEqual(len(response.data['results']), 1)
        else:
            # Resposta não paginada
            self.assertGreaterEqual(len(response.data), 1)
        
    def test_get_character_detail(self):
        """Teste para obter detalhe de um personagem"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Jon Snow')
        self.assertEqual(response.data['external_id'], 583)
        self.assertEqual(response.data['gender'], 'Male')
        self.assertEqual(response.data['culture'], 'Northmen')
        
    def test_character_books_relation(self):
        """Teste para verificar relação entre personagem e livros na API"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['books']), 1)
