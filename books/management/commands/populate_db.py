from books.models import Book
from characters.models import Character
from houses.models import House
import requests
import base64
from django.core.management.base import BaseCommand
from django.utils import timezone
import datetime
import pytz

"""
LIVROS

{
    "url": "https://anapioficeandfire.com/api/books/5",
    "name": "A Feast for Crows",
    "isbn": "978-0553801507",
    "authors": [
        "George R. R. Martin"
    ],
    "numberOfPages": 784,
    "publisher": "Bantam Books",
    "country": "United Status",
    "mediaType": "Hardcover",
    "released": "2005-11-08T00:00:00",
    "characters": [
        "https://anapioficeandfire.com/api/characters/1",
    ],
    "povCharacters": [
        "https://anapioficeandfire.com/api/characters/60",
    ]
}

PERSONAGENS

{
    "url": "https://anapioficeandfire.com/api/characters/1",
    "name": "",
    "gender": "Female",
    "culture": "Braavosi",
    "born": "",
    "died": "",
    "titles": [],
    "aliases": [
        "The Daughter of the Dusk"
    ],
    "father": "",
    "mother": "",
    "spouse": "",
    "allegiances": [],
    "books": [
        "https://anapioficeandfire.com/api/books/5"
    ],
    "povBooks": [],
    "tvSeries": [],
    "playedBy": []
}

CASAS

{
    "url": "https://anapioficeandfire.com/api/houses/362",
    "name": "House Stark of Winterfell",
    "region": "The North",
    "coatOfArms": "A running grey direwolf, on an ice-white field",
    "words": "Winter is Coming",
    "titles": [
        "King in the North",
        "Lord of Winterfell",
        "Warden of the North",
        "King of the Trident"
    ],
    "seats": [
        "Scattered (formerly Winterfell)"
    ],
    "currentLord": "",
    "heir": "",
    "overlord": "https://anapioficeandfire.com/api/houses/16",
    "founded": "Age of Heroes",
    "founder": "https://anapioficeandfire.com/api/characters/209",
    "diedOut": "",
    "ancestralWeapons": [
        "Ice"
    ],
    "cadetBranches": [
        "https://anapioficeandfire.com/api/houses/170",
        "https://anapioficeandfire.com/api/houses/215"
    ],
    "swornMembers": [
        "https://anapioficeandfire.com/api/characters/2",
    ]
}
"""

API_BASE = "https://anapioficeandfire.com/api"
COVER_URL = "https://covers.openlibrary.org/b/isbn/{}-L.jpg"

def extract_id(url):
    return int(url.rstrip('/').split('/')[-1])

def fetch_all(resource):
    results, page = [], 1
    while True:
        resp = requests.get(f"{API_BASE}/{resource}?page={page}&pageSize=50")
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        results.extend(data)
        page += 1
    return results

def download_cover_base64(isbn):
    url = COVER_URL.format(isbn.replace('-', ''))
    resp = requests.get(url)
    if resp.status_code == 200:
        return base64.b64encode(resp.content).decode('ascii')
    return None

class Command(BaseCommand):
    help = "popula o banco com livros, personagens e casas"

    def add_arguments(self, parser):
        parser.add_argument(
            '--tipo',
            choices=['all', 'books', 'characters', 'houses'],
            default='all',
            help='Tipo de dados a serem importados (all, books, characters ou houses)'
        )

    def handle(self, *args, **options):
        tipo = options['tipo']
        
        if tipo == 'all' or tipo == 'characters':
            self.import_characters()
            
        if tipo == 'all' or tipo == 'houses':
            self.import_houses()
            
        if tipo == 'all' or tipo == 'books':
            self.import_books()
            
        print(f">>> importação de {tipo} concluída!")

    def import_characters(self):
        print(">>> importando personagens...")
        chars = fetch_all('characters')
        # criar/atualizar personagens
        for item in chars:
            cid = extract_id(item['url'])
            Character.objects.update_or_create(
                external_id=cid,
                defaults={
                    'name': item.get('name') or None,
                    'gender': item.get('gender') or None,
                    'culture': item.get('culture') or None,
                    'born': item.get('born') or None,
                    'died': item.get('died') or None,
                    'titles': item.get('titles', []),
                    'aliases': item.get('aliases', []),
                    'tv_series': item.get('tvSeries', []),
                    'played_by': item.get('playedBy', []),
                }
            )
        # relacionar familiares e lealdades
        for item in chars:
            char = Character.objects.get(external_id=extract_id(item['url']))
            for rel in ['father', 'mother', 'spouse']:
                url = item.get(rel)
                if url:
                    try:
                        related = Character.objects.get(external_id=extract_id(url))
                        setattr(char, rel, related)
                    except Character.DoesNotExist:
                        pass
            char.save()
            for hurl in item.get('allegiances', []):
                try:
                    house = House.objects.get(external_id=extract_id(hurl))
                    char.allegiances.add(house)
                except House.DoesNotExist:
                    pass

    def import_houses(self):
        print(">>> importando casas...")
        houses = fetch_all('houses')
        # criar/atualizar casas
        for item in houses:
            hid = extract_id(item['url'])
            House.objects.update_or_create(
                external_id=hid,
                defaults={
                    'name': item.get('name'),
                    'region': item.get('region'),
                    'coat_of_arms': item.get('coatOfArms'),
                    'words': item.get('words'),
                    'titles': item.get('titles', []),
                    'seats': item.get('seats', []),
                    'founded': item.get('founded') or None,
                    'died_out': item.get('diedOut') or None,
                    'ancestral_weapons': item.get('ancestralWeapons', []),
                }
            )
        # relacionar casas e personagens
        for item in houses:
            house = House.objects.get(external_id=extract_id(item['url']))
            for rel in ['currentLord', 'heir', 'founder', 'overlord']:
                url = item.get(rel)
                if url:
                    try:
                        if rel == 'overlord':
                            related = House.objects.get(external_id=extract_id(url))
                        else:
                            related = Character.objects.get(external_id=extract_id(url))
                        setattr(house, rel.lower() if rel != 'overlord' else 'overlord', related)
                    except (House.DoesNotExist, Character.DoesNotExist):
                        pass
            house.save()
            for cb in item.get('cadetBranches', []):
                try:
                    branch = House.objects.get(external_id=extract_id(cb))
                    house.cadet_branches.add(branch)
                except House.DoesNotExist:
                    pass
            for sm in item.get('swornMembers', []):
                try:
                    member = Character.objects.get(external_id=extract_id(sm))
                    house.sworn_members.add(member)
                except Character.DoesNotExist:
                    pass

    def import_books(self):
        print(">>> importando livros...")
        resp = requests.get(f"{API_BASE}/books")
        resp.raise_for_status()
        books = resp.json()

        # criar/atualizar livros e relacionar personagens
        for item in books:
            bid = extract_id(item['url'])
            cover = download_cover_base64(item.get('isbn', '')) if item.get('isbn') else None
            released_str = item.get('released')
            released = None
            
            if released_str:
                # Converter para datetime com timezone
                naive_dt = datetime.datetime.fromisoformat(released_str.replace('Z', '+00:00'))
                released = pytz.utc.localize(naive_dt) if naive_dt.tzinfo is None else naive_dt
            book, _ = Book.objects.update_or_create(
                external_id=bid,
                defaults={
                    'name': item.get('name'),
                    'isbn': item.get('isbn'),
                    'authors': item.get('authors', []),
                    'number_of_pages': item.get('numberOfPages'),
                    'publisher': item.get('publisher'),
                    'country': item.get('country'),
                    'media_type': item.get('mediaType'),
                    'released': released,
                    'cover_base64': cover,
                }
            )
            for url in item.get('characters', []):
                try:
                    book.characters.add(Character.objects.get(external_id=extract_id(url)))
                except Character.DoesNotExist:
                    pass
            for url in item.get('povCharacters', []):
                try:
                    book.pov_characters.add(Character.objects.get(external_id=extract_id(url)))
                except Character.DoesNotExist:
                    pass
