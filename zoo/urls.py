from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name="index"),
    path('animals', views.animals, name="animals"),
    path('animals/<int:id>', views.show_animal, name="animal"),
    path('animals/<int:id>/move', views.move_animal, name="move_animal"),
    path('animals/<int:id>/medical-reports', views.add_medical_report, name="add_medical_report"),
    path('animals/<int:id>/add_fav', views.add_fav, name="add_fav"),
    path('animals/<int:id>/remove_fav', views.remove_fav, name="remove_fav"),
    path('enclosures/<int:id>', views.show_enclosure, name="enclosure"),
    path('favourite', views.favourite, name="favourite"),
]
