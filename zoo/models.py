from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Enclosure(models.Model):
    capacity = models.IntegerField(default=0)

    def animals_count(self):
        return self.animal_set.count()

    def __str__(self):
        return f"{self.capacity}-animal enclosure ({self.animals_count()} occupants)"


class Species(models.Model):

    class DietType(models.TextChoices):
        CARNIVORE = 'Carnivore'
        HERBIVORE = 'Herbivore'
        OMNIVORE  = 'Omnivore'

    diet_type = models.CharField(max_length=9, choices=DietType.choices)
    name      = models.CharField(max_length=200)

    def __str__(self):
        return f"Species {self.name} (type {self.diet_type})"


class Animal(models.Model):

    class Gender(models.TextChoices):
        MALE   = 'Male'
        FEMALE = 'Female'

    name          = models.CharField(max_length=200)
    species       = models.ForeignKey(Species, on_delete=models.CASCADE)
    enclosure     = models.ForeignKey(Enclosure, on_delete=models.SET_NULL, null=True)
    date_of_birth = models.DateField(null=True)
    gender        = models.CharField(max_length=6, choices=Gender.choices)
    image         = models.ImageField(upload_to='images/')

    def __str__(self):
        return f"{self.name} {'F' if self.gender == 'Female' else 'M'} (Species: {self.species})"

    @property
    def age(self):
        import datetime
        if self.date_of_birth:
            return int((datetime.date.today() - self.date_of_birth).days / 365.25)
        else:
            return "Unknown"

    def clean(self):
        if self.enclosure and self.enclosure.animals_count() == self.enclosure.capacity:
            raise ValidationError('Destination enclosure is already full.')


class MedicalReport(models.Model):

    author     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    animal     = models.ForeignKey(Animal, on_delete=models.CASCADE)
    title      = models.CharField(max_length=250)
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Medical Report for {self.animal} by {self.author}"

