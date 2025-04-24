from django.db import models

"""
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

class House(models.Model):
    external_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=100, blank=True, null=True)
    coat_of_arms = models.TextField(blank=True, null=True)
    words = models.CharField(max_length=255, blank=True, null=True)

    titles = models.JSONField(default=list, blank=True)
    seats = models.JSONField(default=list, blank=True)
    founded = models.CharField(max_length=255, blank=True, null=True)
    died_out = models.CharField(max_length=255, blank=True, null=True)
    ancestral_weapons = models.JSONField(default=list, blank=True)

    current_lord = models.ForeignKey(
        'characters.Character', on_delete=models.SET_NULL,
        related_name='current_lord_of', null=True, blank=True
    )
    heir = models.ForeignKey(
        'characters.Character', on_delete=models.SET_NULL,
        related_name='heir_of', null=True, blank=True
    )
    overlord = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        related_name='vassals', null=True, blank=True
    )
    founder = models.ForeignKey(
        'characters.Character', on_delete=models.SET_NULL,
        related_name='founded_houses', null=True, blank=True
    )

    cadet_branches = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='parent_houses',
        blank=True
    )
    sworn_members = models.ManyToManyField(
        'characters.Character',
        related_name='sworn_houses',
        blank=True
    )

    def __str__(self):
        return self.name
