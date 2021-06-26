from django.shortcuts import render
from django.db import connection
from random import sample

# Create your views here.
def index(request):
    data = {}

    try:
        with connection.cursor() as cursor:

            cursor.execute("SELECT count(*) as tt FROM HABITACION")
            count_hab = cursor.fetchone()[0]
            cursor.execute("SELECT * FROM HABITACION")
            habitaciones = list(cursor.fetchall())
            if int(count_hab) < 3:     
                print('soy menor')        
                rand_hab = sample(habitaciones, count_hab)
                print(rand_hab)
                data["habitaciones"] = rand_hab
                print(data["habitaciones"])
            else:
                rand_hab = sample(habitaciones, 3)
                data["habitaciones"] = rand_hab 
            print('imprimo cant hab:', count_hab)                   
            cursor.execute("SELECT count(*) FROM SERVICIO_ADICIONAL WHERE MOSTRAR_INICIO = 1")
            count_serv = cursor.fetchone()[0]
            print('cantidad serv', count_serv)
            cursor.execute("SELECT * FROM SERVICIO_ADICIONAL WHERE MOSTRAR_INICIO = %s", [1])
            servicios_adicionales = list(cursor.fetchall())
            if int(count_serv) <3:             
                rand_serv = sample(servicios_adicionales, count_serv)
                data["servicios_adicionales"] = rand_serv
            else:
                rand_serv = sample(servicios_adicionales, 3)
                data["servicios_adicionales"] = rand_serv
    except Exception as e:
        print(e)
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