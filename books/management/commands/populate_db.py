import os
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
Rodar 2 vezes para fazer as ligações entre personagens e livros

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
    "titles": ["The Daughter of the Dusk"],
    "aliases": [
        "The Daughter of the Dusk"
    ],
    "father": "",
    "mother": "",
    "spouse": "",
    "allegiances": ["https://anapioficeandfire.com/api/houses/362"],
    "books": [
        "https://anapioficeandfire.com/api/books/5"
    ],
    "povBooks": ["https://anapioficeandfire.com/api/books/5"],
    "tvSeries": ["Game of Thrones"],
    "playedBy": ["Emilia Clarke"]
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

MAX_PAGES = 10
API_BASE = "https://anapioficeandfire.com/api"
COVER_URL = "https://covers.openlibrary.org/b/isbn/{}-L.jpg"

def extract_id(url):
    return int(url.rstrip('/').split('/')[-1])

def fetch_all(resource):
    results, page = [], 1
    for page in range(1, MAX_PAGES + 1):
        resp = requests.get(f"{API_BASE}/{resource}?page={page}&pageSize=50")
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        results.extend(data)
    return results

def download_cover_base64(isbn):
    url = COVER_URL.format(isbn.replace('-', ''))
    resp = requests.get(url)
    if resp.status_code == 200:
        return base64.b64encode(resp.content).decode('ascii')
    return None


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            choices=['all', 'books', 'characters', 'houses'],
            default='all',
        )

    def handle(self, *args, **options):
        tipo = options['type']
        
        if tipo == 'all' or tipo == 'characters':
            self.import_characters()
            
        if tipo == 'all' or tipo == 'houses':
            self.import_houses()
            self.relate_characters_to_houses()
            
        if tipo == 'all' or tipo == 'books':
            self.import_books()
            if tipo == 'books':
                self.get_characters()
            self.relate_characters_to_books()
            
        print(f">>> importação de {tipo} concluída!")

    def import_characters(self):
        print(">>> importando personagens...")
        self.get_characters()
        
        for item in self.chars_json:
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
            
        for item in self.chars_json:
            char = Character.objects.get(external_id=extract_id(item['url']))
            for i in ['father', 'mother', 'spouse']:
                url = item.get(i)
                if url:
                    related = Character.objects.filter(external_id=extract_id(url)).first()
                    if related:
                        setattr(char, i, related)
            char.save()
            
    def relate_characters_to_houses(self):
        for item in self.chars_json:
            char = Character.objects.get(external_id=extract_id(item['url']))
            for i in item.get('allegiances', []):
                house = House.objects.filter(external_id=extract_id(i)).first()
                if house:
                    char.allegiances.add(house)
                
                
    def relate_characters_to_books(self):
        for item in self.chars_json:
            char = Character.objects.get(external_id=extract_id(item['url']))
            for i in item.get('books', []):
                book = Book.objects.filter(external_id=extract_id(i)).first()
                if book:
                    char.books.add(book)
                    
            for i in item.get('povBooks', []):
                book = Book.objects.filter(external_id=extract_id(i)).first()
                if book:
                    char.pov_books.add(book)
                

    def import_houses(self):
        print(">>> importando casas...")
        self.get_houses()
        
        for item in self.houses_json:
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
            
        for item in self.houses_json:
            house = House.objects.get(external_id=extract_id(item['url']))
            for rel in ['currentLord', 'heir', 'founder', 'overlord']:
                url = item.get(rel)
                if url:
                    if rel == 'overlord':
                        related = House.objects.filter(external_id=extract_id(url)).first()
                    else:
                        related = Character.objects.filter(external_id=extract_id(url)).first()
                    
                    if related:
                        setattr(house, rel.lower() if rel != 'overlord' else 'overlord', related)
            house.save()
            for cb in item.get('cadetBranches', []):
                branch = House.objects.filter(external_id=extract_id(cb)).first()
                if branch:
                    house.cadet_branches.add(branch)
            for sm in item.get('swornMembers', []):
                member = Character.objects.filter(external_id=extract_id(sm)).first()
                if member:
                    house.sworn_members.add(member)


    def get_houses(self):
        self.houses_json = fetch_all('houses')
        return self.houses_json
    
    
    def get_characters(self):
        self.chars_json = fetch_all('characters')
        return self.chars_json
    
    
    def get_books(self):
        self.books_json = fetch_all('books')
        return self.books_json
    
        
    def import_books(self):
        print(">>> importando livros...")
        self.get_books()

        for item in self.books_json:
            bid = extract_id(item['url'])
            cover = download_cover_base64(item.get('isbn', '')) if item.get('isbn') else None
            released_str = item.get('released')
            released = None
            
            if released_str:
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
                    'amazon_link': f"https://www.amazon.com.br/s?k={item.get('isbn').replace('-', '')}",
                }
            )
            for url in item.get('characters', []):
                character = Character.objects.filter(external_id=extract_id(url)).first()
                if character:   
                    book.characters.add(character)
            for url in item.get('povCharacters', []):
                character = Character.objects.filter(external_id=extract_id(url)).first()
                if character:
                    book.pov_characters.add(character)
    



