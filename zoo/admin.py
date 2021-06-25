from django.contrib import admin
from .models import Animal, Enclosure, Species


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    fields = ('name', 'species', 'date_of_birth', 'gender', 'image')


admin.site.register(Enclosure)
admin.site.register(Species)
