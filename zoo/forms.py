from django import forms
from .models import Animal, MedicalReport


class FilterAnimalsForm(forms.Form):
    CHOICES = [('None', '--------')] + Animal.Gender.choices
    gender  = forms.ChoiceField(
        label="Filter by gender", 
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
            'enclosure': ''
        }


class AddMedicalReportForm(forms.ModelForm):
    class Meta:
        model   = MedicalReport
        fields  = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }
