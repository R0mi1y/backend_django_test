from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from books.models import Book
from characters.models import Character

class BookViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
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
        self.book.pov_characters.add(self.character)

    def test_list_books(self):
        url = reverse('book-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_retrieve_book(self):
        url = reverse('book-detail', args=[self.book.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], "Test Book")

    def test_all_pov_characters(self):
        url = reverse('book-all-pov-characters')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_pov_characters(self):
        url = reverse('book-pov-characters', args=[self.book.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_cover(self):
        url = reverse('book-cover', args=[self.book.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
