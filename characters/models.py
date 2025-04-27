from itertools import chain
from django.db import models

from books.models import Book

"""
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
"""

class Character(models.Model):
    external_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True)
    culture = models.CharField(max_length=255, blank=True, null=True)
    born = models.CharField(max_length=255, blank=True, null=True)
    died = models.CharField(max_length=255, blank=True, null=True)

    titles = models.JSONField(default=list, blank=True)
    aliases = models.JSONField(default=list, blank=True)

    father = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        related_name='children_father', null=True, blank=True
    )
    mother = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        related_name='children_mother', null=True, blank=True
    )
    spouse = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        related_name='spouses', null=True, blank=True
    )

    allegiances = models.ManyToManyField(
        'houses.House',
        related_name='members',
        blank=True
    )
    books = models.ManyToManyField(
        'books.Book',
        related_name='book_characters',
        blank=True
    )
    pov_books = models.ManyToManyField(
        'books.Book',
        related_name='book_pov_characters',  
        blank=True
    )

    tv_series = models.JSONField(default=list, blank=True)
    played_by = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name or f"Character {self.external_id}"
    
