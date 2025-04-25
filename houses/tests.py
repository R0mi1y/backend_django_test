from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from django.contrib.auth.models import User
from oauth2_provider.models import Application, AccessToken
from .models import House
from characters.models import Character


class HouseModelTest(TestCase):
    """Testes para o modelo House"""
    
    def setUp(self):
        # Criar casa principal
        self.house_data = {
            'external_id': 362,
            'name': 'House Stark of Winterfell',
            'region': 'The North',
            'coat_of_arms': 'A running grey direwolf, on an ice-white field',
            'words': 'Winter is Coming',
            'titles': [
                'King in the North',
                'Lord of Winterfell',
                'Warden of the North',
                'King of the Trident'
            ],
            'seats': ['Winterfell'],
            'founded': 'Age of Heroes',
            'ancestral_weapons': ['Ice']
        }
        self.house = House.objects.create(**self.house_data)
        
        # Criar personagens para relações
        self.lord = Character.objects.create(
            external_id=339,
            name='Eddard Stark',
            gender='Male',
            culture='Northmen'
        )
        
        self.heir = Character.objects.create(
            external_id=583,
            name='Jon Snow',
            gender='Male',
            culture='Northmen'
        )
        
        self.founder = Character.objects.create(
            external_id=209,
            name='Bran the Builder',
            gender='Male',
            culture='Northmen'
        )
        
        # Criar casa vassala
        self.vassal_house = House.objects.create(
            external_id=170,
            name='House Karstark of Karhold',
            region='The North',
            words='The Sun of Winter'
        )
        
        # Estabelecer relações
        self.house.current_lord = self.lord
        self.house.heir = self.heir
        self.house.founder = self.founder
        self.house.save()
        
        self.house.sworn_members.add(self.lord)
        self.house.sworn_members.add(self.heir)
        
        self.vassal_house.overlord = self.house
        self.vassal_house.save()
        
        self.house.cadet_branches.add(self.vassal_house)
    
    def test_house_creation(self):
        """Teste de criação da casa"""
        self.assertEqual(House.objects.count(), 2)  # 2 casas criadas no setup
        self.assertEqual(self.house.name, 'House Stark of Winterfell')
        self.assertEqual(self.house.external_id, 362)
        self.assertEqual(self.house.region, 'The North')
        self.assertEqual(self.house.words, 'Winter is Coming')
        
    def test_house_relations(self):
        """Teste de relacionamentos da casa"""
        self.assertEqual(self.house.current_lord.name, 'Eddard Stark')
        self.assertEqual(self.house.heir.name, 'Jon Snow')
        self.assertEqual(self.house.founder.name, 'Bran the Builder')
        self.assertEqual(self.house.sworn_members.count(), 2)
        self.assertEqual(self.house.cadet_branches.count(), 1)
        self.assertEqual(self.house.cadet_branches.first().name, 'House Karstark of Karhold')
        
        # Testar relação de vassalagem
        self.assertEqual(self.vassal_house.overlord.name, 'House Stark of Winterfell')
        
    def test_house_array_fields(self):
        """Teste dos campos JSON da casa"""
        self.assertEqual(len(self.house.titles), 4)
        self.assertEqual(len(self.house.seats), 1)
        self.assertEqual(len(self.house.ancestral_weapons), 1)
        self.assertIn('Ice', self.house.ancestral_weapons)
        self.assertIn('King in the North', self.house.titles)
        
    def test_house_str_method(self):
        """Teste do método __str__ do modelo House"""
        self.assertEqual(str(self.house), 'House Stark of Winterfell')


class HouseAPITest(APITestCase):
    """Testes para a API de Houses"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Criar casa para teste
        self.house = House.objects.create(
            external_id=362,
            name='House Stark of Winterfell',
            region='The North',
            coat_of_arms='A running grey direwolf, on an ice-white field',
            words='Winter is Coming',
            titles=[
                'King in the North',
                'Lord of Winterfell'
            ],
            seats=['Winterfell'],
            founded='Age of Heroes',
            ancestral_weapons=['Ice']
        )
        
        # Criar personagem para teste de relacionamento
        self.character = Character.objects.create(
            external_id=339,
            name='Eddard Stark',
            gender='Male',
            culture='Northmen'
        )
        
        # Relacionar personagem e casa
        self.house.current_lord = self.character
        self.house.save()
        self.house.sworn_members.add(self.character)
        
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
        self.list_url = reverse('house-list')
        self.detail_url = reverse('house-detail', args=[self.house.id])
    
    def test_get_house_list(self):
        """Teste para obter lista de casas"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # A resposta pode ser paginada ou não
        if isinstance(response.data, dict) and 'results' in response.data:
            # Resposta paginada
            self.assertGreaterEqual(len(response.data['results']), 1)
        else:
            # Resposta não paginada
            self.assertGreaterEqual(len(response.data), 1)
        
    def test_get_house_detail(self):
        """Teste para obter detalhe de uma casa"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'House Stark of Winterfell')
        self.assertEqual(response.data['external_id'], 362)
        self.assertEqual(response.data['region'], 'The North')
        self.assertEqual(response.data['words'], 'Winter is Coming')
        
    def test_house_relationships_in_api(self):
        """Teste para verificar relações da casa na API"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['current_lord'])
        self.assertEqual(len(response.data['sworn_members']), 1)
