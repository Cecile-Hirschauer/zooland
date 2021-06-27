from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required, login_required
from .models import Enclosure, Animal, MedicalReport, Species, User, FavAnimal
from .forms import *
from .helpers import form_errors_to_messages
from django.contrib import messages
from django.db import IntegrityError
from django.urls import reverse

def index(request): # Page d'accueil / index
    context = { 'enclosures':  Enclosure.objects.all() }

    return render(request, 'zoo/index.html', context)


def animals(request): # Afficher les animaux selon filtre(s) appliqué(s)
    animals_all = Animal.objects.all()
    gender = request.GET.get('gender')
    dietType = request.GET.get('dietType')

    # Si deux filtres, ie sexe et régime alimentaire
    if gender and gender in Animal.Gender and dietType and dietType in Species.DietType:
        animals = Animal.objects.filter(gender=gender, species__diet_type=dietType)
        

    # Si filtre sexe
    elif gender and gender in Animal.Gender:
        animals = Animal.objects.filter(gender=gender)

    # Si filtre régime alimentaire
    elif dietType and dietType in Species.DietType:
        diet_type_list = []
        for animal in animals_all:
            if animal.species.diet_type == dietType:
                diet_type_list.append(animal)
        animals = diet_type_list

    # Si aucun filtre
    else:
        animals = animals_all

    context = { 'animals': animals, 'form_gender': FilterAnimalsGenderForm(request.GET), 'form_species': FilterAnimalsSpeciesForm(request.GET) }

    return render(request, 'zoo/animals.html', context)


def show_enclosure(request, id): # Afficher l'enclos et les animaux qu'il contient
    enclosure = get_object_or_404(Enclosure, id=id)

    context = {
        'enclosure': enclosure,
        'occupants': Animal.objects.filter(enclosure=enclosure)
    }

    return render(request, 'zoo/show_enclosure.html', context)


def show_animal(request, id): # Afficher le profil de l'animal de l'ID associé et divers formulaires
    animal = get_object_or_404(Animal, id=id)
    
    # afficher formulaire add favori si l'animal n'est pas déjà dans les favoris
    favorites = FavAnimal.objects.filter(fav_animal=animal.id)
    my_favorite = False
    for favorite in favorites:
        if favorite.fav_animal == animal:
            my_favorite = True
            
    context = {
        'animal': animal,
        'reports': MedicalReport.objects.filter(animal=animal),
        'move_form': MoveEnclosureForm(instance=animal),
        'medical_form': AddMedicalReportForm(),
        'form3': FavAnimalForm(),
        'favorite': my_favorite
    }

    return render(request, 'zoo/show_animal.html', context)


@permission_required('zoo.change_animal') # Déplacer un animal d'un enclos à l'autre
def move_animal(request, id):
    animal = get_object_or_404(Animal, id=id) # animal en question (celui qui s'affiche sur la page)

    if request.method == 'POST':
        
        form = MoveEnclosureForm(request.POST, instance=animal)
        new_enclosure_id = request.POST['enclosure'] # enclos dans lequel on veut mettre l'animal (champ dans formulaire)
        new_enclosure = Enclosure.objects.get(pk=new_enclosure_id)
        if form.is_valid():
            
            if new_enclosure:

                new_enclosure_occupants = Animal.objects.filter(enclosure=new_enclosure_id) # animaux déjà dans l'enclos en question
                list_occupants = []
                carnivore = False
                for occupant in new_enclosure_occupants:
                    list_occupants.append(occupant)

                if "Carnivore" in str(list_occupants):
                    carnivore = True
                    
                # si pas de message d'erreur, ie le nouvel enclos n'est pas complet, et
                # si animal est herbivore ou omnivore et le nouvel enclos ne contient aucun carnivore (carnivore=False)
                if form.cleaned_data['enclosure']\
                    and animal.species.diet_type != "Carnivore"\
                    and not carnivore:
                    form.save()
                    messages.info(request, f"{animal.name} is now in enclosure #{new_enclosure.id}")
                
                # si pas de message d'erreur, ie le nouvel enclos n'est pas complet, et
                # si animal est carnivore et nouvel enclos est vide
                elif form.cleaned_data['enclosure']\
                    and animal.species.diet_type == "Carnivore"\
                    and (carnivore or len(list_occupants) == 0):
                    form.save()
                    messages.info(request, f"{animal.name} is now in enclosure #{new_enclosure.id}")
                else:
                    messages.error(request, 'Danger zone ! ')
            
            # si message d'erreur, ie le nouvel enclos est complet
            else:
                form_errors_to_messages(request, form)
            
        else:
            form_errors_to_messages(request, form)  

    return redirect('animal', id=id)



@permission_required('zoo.add_medicalreport') # Affichage du formulaire si l'utilisateur est véto
def add_medical_report(request, id):
    animal = get_object_or_404(Animal, id=id)

    if request.method == 'POST':
        form = AddMedicalReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.author = request.user
            report.animal = animal
            report.save()
        else:
            form_errors_to_messages(request, form)         

    return redirect('animal', id=id)


@login_required
def add_fav(request, id): # Ajout de l'animal aux favoris de l'utilisateur connecté
    animal = get_object_or_404(Animal, id=id)

    if request.method == 'POST':
        form_fav_animal = FavAnimalForm(request.POST)
        if form_fav_animal.is_valid(): # formulaire est valide / l'ajout se fait si ...
            
            current_user = request.user # si utilisateur y en a
            user_obj = User.objects.filter(id=current_user.id)
            fav_animal_obj = FavAnimal(fav_animal=animal, reg_user=user_obj[0])
            try:
                fav_animal_obj.save()
                messages.info(request, f"Added to Favourites!")
                return redirect('favourite')

            except IntegrityError as e:
                messages.error(request, f"Had already been added to Favourites!")
            
        else:
            form_errors_to_messages(request, form_fav_animal)  
            

    return redirect('animal', id=id)



@login_required
def remove_fav(request, id):
    # remove animal from favourites with a warning message
    animal = Animal.objects.get(id=id)
    if request.method =="POST":
        current_user = request.user # si utilisateur y en a
        user_obj = User.objects.filter(id=current_user.id)
        fav_animal_obj = FavAnimal.objects.filter(fav_animal=animal,reg_user=user_obj[0])
        print(fav_animal_obj)
        fav_animal_obj.delete()
        messages.warning(request, f"{animal.name} has been removed from your favorites!")
        return redirect('favourite')
    return redirect('animal', id=id)
        


@login_required
def favourite(request):
    current_user = request.user
    animal_objs = FavAnimal.objects.filter(reg_user=current_user)
    animal_obj_ids = []
    for i in range(len(animal_objs)):
        animal_obj_id = animal_objs[i].fav_animal.id
        animal_obj_ids.append(animal_obj_id)
    fav_animals = []
    for animal_obj_id in animal_obj_ids:
        fav_animal = Animal.objects.filter(id=animal_obj_id)
        fav_animals.append(fav_animal[0])
    context = {'animals': fav_animals }

    return render(request, 'zoo/favourite.html', context)
    