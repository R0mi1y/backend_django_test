from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from characters.models import Character
from books.models import Book

class CharacterViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.character = Character.objects.create(
            external_id=1,
            name="Test Character",
            gender="Male",
            culture="Test Culture",
            born="Test Born",
            died="Test Died",
            titles=["Test Title"],
            aliases=["Test Alias"],
            tv_series=[],
            played_by=[]
        )
        self.book = Book.objects.create(
            external_id=1,
            name="Test Book",
            isbn="1234567890",
            authors=["Test Author"],
            number_of_pages=100,
            publisher="Test Publisher",
            country="Test Country",
            media_type="Hardcover",
            released="2024-01-01T00:00:00Z",
            cover_base64="base64string"
        )
        self.character.books.add(self.book)
        self.character.pov_books.add(self.book)

    def test_list_characters(self):
        url = reverse('character-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_retrieve_character(self):
        url = reverse('character-detail', args=[self.character.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], "Test Character")

    def test_character_books(self):
        url = reverse('character-books', args=[self.character.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_character_pov_books(self):
        url = reverse('character-pov-books', args=[self.character.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
