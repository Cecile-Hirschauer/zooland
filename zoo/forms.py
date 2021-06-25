from django import forms
from .models import Animal, MedicalReport, Species, FavAnimal


class FilterAnimalsGenderForm(forms.Form):
    CHOICES = [('None', '--------')] + Animal.Gender.choices
    gender  = forms.ChoiceField(
        label="Filter by gender", 
        choices=CHOICES, 
        required=False, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class FilterAnimalsSpeciesForm(forms.Form):
    CHOICES = [('None', '--------')] + Species.DietType.choices
    dietType  = forms.ChoiceField(
        label="Filter by species", 
        choices=CHOICES, 
        required=False, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class MoveEnclosureForm(forms.ModelForm):
    class Meta:
        model   = Animal
        fields  = ['enclosure']
        widgets = {
            'enclosure': forms.Select(attrs={'class': 'form-control'}),
        }
        labels  = {
            'enclosure': 'Enclosures'
        }


class AddMedicalReportForm(forms.ModelForm):
    class Meta:
        model   = MedicalReport
        fields  = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }

class FavAnimalForm(forms.Form):
    class Meta:
        model   = Animal
        fields = ['name']
        # widgets = {'name': forms.HiddenInput()}
        
class RemoveFavAnimalForm(forms.Form):
    class Meta:
        model   = FavAnimal
        fields = ['id']
