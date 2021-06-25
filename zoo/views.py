from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required, login_required
from .models import Enclosure, Animal, MedicalReport
from .forms import FilterAnimalsForm, MoveEnclosureForm, AddMedicalReportForm
from .helpers import form_errors_to_messages


def index(request):
    context = { 'enclosures':  Enclosure.objects.all() }

    return render(request, 'zoo/index.html', context)


def animals(request):
    gender = request.GET.get('gender')
    if gender is not None and gender in Animal.Gender:
        animals = Animal.objects.filter(gender=gender)
    else:
        animals = Animal.objects.all()

    context = { 'animals': animals, 'form': FilterAnimalsForm(request.GET) }

    return render(request, 'zoo/animals.html', context)


def show_enclosure(request, id):
    enclosure = get_object_or_404(Enclosure, id=id)

    context = {
        'enclosure': enclosure,
        'occupants': Animal.objects.filter(enclosure=enclosure)
    }

    return render(request, 'zoo/show_enclosure.html', context)


def show_animal(request, id):
    animal = get_object_or_404(Animal, id=id)

    context = {
        'animal': animal,
        'reports': MedicalReport.objects.filter(animal=animal),
        'move_form': MoveEnclosureForm(instance=animal),
        'medical_form': AddMedicalReportForm()
    }

    return render(request, 'zoo/show_animal.html', context)


@permission_required('zoo.change_animal') 
def move_animal(request, id):
    animal = get_object_or_404(Animal, id=id)

    if request.method == 'POST':
        form = MoveEnclosureForm(request.POST, instance=animal)
        if form.is_valid():
            form.save()
        else:
            form_errors_to_messages(request, form)  

    return redirect('animal', id=id)


@permission_required('zoo.add_medicalreport') 
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
