from zoo.models import Species, Animal
from django.test import TestCase
from unittest.mock import patch
from django.test.client import Client

# Create your tests here.
class RenderViewTestCase(TestCase): # test le render de la fonction index de ma view
    def setUp(self): # fonction de mise en place"
        self.client = Client()
        
    def test_render(self): # fonction de test
        url = '' # url que je vais tester
        response = self.client.get(url) # réponse à ma demande
        self.assertEqual(response.status_code, 200) # j'emets l'hypothèse que mon code réponse est 200
        self.assertTemplateUsed(response, 'zoo/base.html')
        self.assertTemplateUsed(response, 'zoo/index.html')
        self.assertContains(response, "Test de texte")
        

class calculAgeNonetestCase(TestCase):
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

class SuccessMessageTestCase(TestCase):
   pass


class MoveEnclosureViewTestCase(TestCase): # test le render de la fonction index de ma view
    def setUp(self): # fonction de mise en place"
        self.client = Client()
        
    def test_render(self): # fonction de test
        url = '' # url que je vais tester
        response = self.client.get(url) # réponse à ma demande
        self.assertEqual(response.status_code, 200) # j'emets l'hypothèse que mon code réponse est 200
        self.assertTemplateUsed(response, 'zoo/base.html')
        self.assertTemplateUsed(response, 'zoo/index.html')
        self.assertContains(response, "Test de texte")