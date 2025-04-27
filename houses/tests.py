from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from houses.models import House

class HouseViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.house = House.objects.create(
            external_id=1,
            name="Test House",
            region="Test Region",
            coat_of_arms="Test Coat of Arms",
            words="Test Words",
            titles=["Test Title"],
            seats=["Test Seat"],
            founded="Test Founded",
            died_out="Test Died Out",
            ancestral_weapons=["Test Weapon"]
        )

    def test_list_houses(self):
        url = reverse('house-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_retrieve_house(self):
        url = reverse('house-detail', args=[self.house.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], "Test House")
