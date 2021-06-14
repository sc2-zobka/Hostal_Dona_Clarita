from django.urls import path
from .views import index, acercade, habitaciones, det_habitacion, contacto
urlpatterns = [
    path('', index, name="index"),
    path('acerca-de/', acercade, name="acercade"),
    path('habitaciones/', habitaciones, name="habitaciones"),
    path('det-habitacion/', det_habitacion, name="det-habitacion"),
    path('contacto/', contacto, name="contacto"),

]
