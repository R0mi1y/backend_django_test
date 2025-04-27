from django.contrib import admin
from .models import Character

class CharacterAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'name')
    search_fields = ('name', 'external_id')
    list_filter = ('books', 'pov_books')

admin.site.register(Character, CharacterAdmin)
