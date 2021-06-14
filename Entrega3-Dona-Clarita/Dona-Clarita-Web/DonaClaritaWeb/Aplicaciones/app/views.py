from django.shortcuts import render
from django.db import connection
from random import sample

# Create your views here.
def index(request):
    data = {}

    try:
        with connection.cursor() as cursor:

            cursor.execute("SELECT count(*) as tt FROM APP_HABITACION")
            count_hab = cursor.fetchone()
            cursor.execute("SELECT * FROM APP_HABITACION")
            habitaciones = list(cursor.fetchall())
            if count_hab:
                if count_hab[0] <3:             
                    rand_hab = sample(habitaciones, count_hab[0])
                    data["habitaciones"] = rand_hab
                else:
                    rand_hab = sample(habitaciones, count_hab[0])
                    data["habitaciones"] = rand_hab                    

            cursor.execute("SELECT * FROM APP_SERVICIOADICIONAL WHERE MOSTRAR_INICIO = %s", [1])
            servicios_adicionales = list(cursor.fetchall())

            rand_serv = sample(servicios_adicionales, 3)
            data["servicios_adicionales"] = rand_serv
    except:
        pass

    return render(request, 'app/index.html', data)

def acercade(request):
    return render(request, 'app/acercade.html')

def habitaciones(request):
    return render(request, 'app/habitaciones.html')

def det_habitacion(request):
    return render(request, 'app/det-habitacion.html')

def contacto(request):
    return render(request, 'app/contacto.html')