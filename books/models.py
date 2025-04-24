from django.db import models

"""
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
"""

class Book(models.Model):
    external_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20)
    authors = models.JSONField(default=list)
    number_of_pages = models.IntegerField()
    publisher = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    media_type = models.CharField(max_length=100)
    released = models.DateTimeField()

    cover_base64 = models.TextField(blank=True, null=True)
    characters = models.ManyToManyField(
        'characters.Character',
        related_name='character_books',
        blank=True
    )
    pov_characters = models.ManyToManyField(
        'characters.Character',
        related_name='character_pov_books',
        blank=True
    )

    def __str__(self):
        return self.name
