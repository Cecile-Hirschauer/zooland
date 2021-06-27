from typing import Reversible
from django.template.defaultfilters import pluralize
from zoo.models import *
from django.test import TestCase
from unittest.mock import patch
from django.test.client import Client
from django. urls import reverse

# Create your tests here.
class RenderViewTestCase(TestCase): # test le render de la fonction index de ma view
    def setUp(self): # fonction de mise en place"
        self.client = Client()
        enclosure = Enclosure(name="Singes", capacity=6)
        enclosure.save()
        
    def test_render(self): # fonction de test
        url = '' # url que je vais tester
        response = self.client.get(url) # réponse à ma demande
        self.assertEqual(response.status_code, 200) # j'emets l'hypothèse que mon code réponse est 200
        self.assertTemplateUsed(response, 'zoo/base.html')
        self.assertTemplateUsed(response, 'zoo/index.html')
        self.assertContains(response, "Enclosures")
        singes = Enclosure.objects.first()
        self.assertEqual(singes.name, "Singes")
        self.assertContains(response, "Singes")

        

class calculAgeNoneTestCase(TestCase):
    def setUp(self):
        species_a = Species()
        species_a.name = "Dauphin"
        species_a.diet_type = Species.DietType.CARNIVORE
        species_a.save()
        
        animal_a = Animal(name="Fliper", species = species_a, enclosure=None, date_of_birth=None, image=None)
        animal_a.save()
        
    def test_age_is_none(self):
        fliper = Animal.objects.first()
        age = fliper.age
        self.assertEqual(age, "Unknown")
        

class MoveAnimalEnclosueTestCase(TestCase):
    def setUp(self):
        species_a = Species()
        species_a.name = "Dauphin"
        species_a.diet_type = Species.DietType.CARNIVORE
        species_a.save()
        
        enclosure_1 = Enclosure(name="Carnivores", capacity=5)
        enclosure_2 = Enclosure(name="Grand bassin", capacity=2)
        enclosure_1.save()
        enclosure_2.save()
        
        animal_a = Animal(name="Fliper", species = species_a, enclosure=enclosure_1, date_of_birth=None, image='image')
        animal_a.save()
        
    def test_move_animal(self):
        fliper = Animal.objects.first()
        response = self.client.post(
            reverse('move_animal', 
                    kwargs = {'id': fliper.id}), 
                    {'enclosure': 2}
        )
        print(response)
        self.assertEqual(response.status_code, 302)

        fliper.refresh_from_db()
        # self.assertEqual(fliper.enclosure, enclosure) 

    def test_can_send_message(self):
        fliper = Animal.objects.first()
        data = {
            "enclosure": 1,
        }
        response = self.client.get(reverse('animal', 
                           kwargs = {'id': fliper.id}))
        self.assertTemplateUsed(response, "zoo/show_animal.html")
        self.assertContains(response, "1")
        response = self.client.post(reverse('animal', 
                           kwargs = {'id': fliper.id}), data=data)
        self.assertEqual(Enclosure.objects.count(), 2)
        self.assertRedirects(response, reverse('animal', 
                                               kwargs = {'id': fliper.id}))
        
        
class PluralizeTest(TestCase):
    def setUp(self):
        self.client= Client()
 
    def test_pluralize_error(self):
        self.assertEqual(pluralize(object, 's'), '')

