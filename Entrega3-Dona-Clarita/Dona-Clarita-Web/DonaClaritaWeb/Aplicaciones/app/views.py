from django.shortcuts import render
from django.db import connection
from random import sample

# Create your views here.
def index(request):
    data = {}

    opiniones = None

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT TM.VALOR_PESO, TM.CODIGO_MONEDA
                FROM TIPO_MONEDA TM 
                JOIN CONFIGURACION CO ON TM.CODIGO_MONEDA = DIVISA_PRINCIPAL
            """)
            divisa_principal = cursor.fetchone()
            print(divisa_principal)
            data["codigo_moneda_p"] = divisa_principal[1]

            cursor.execute("""
                SELECT TM.VALOR_PESO, TM.CODIGO_MONEDA
                FROM TIPO_MONEDA TM  
                JOIN CONFIGURACION CO ON TM.CODIGO_MONEDA = DIVISA_SECUNDARIA
            """)
            divisa_secundaria = cursor.fetchone()
            print(divisa_secundaria)
            data["codigo_moneda_s"] = divisa_secundaria[1]

            cursor.execute("SELECT count(*) as tt FROM HABITACION")
            count_hab = cursor.fetchone()[0]
            
            cursor.execute(f"""
                SELECT ID_HABITACION AS "0", NUMERO_HABITACION AS "1", PRECIO * {divisa_principal[0]} AS "2", ROUND(PRECIO / {divisa_secundaria[0]}, 2) AS "3", 
                DESCRIPCION AS "4", ID_ESTADO_HABITACION AS "5", ID_TIPO_HABITACION AS "6", IMAGEN AS "7"
                FROM HABITACION 
                WHERE MUESTRA_MENU = 1
            """)
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
            
            cursor.execute("SELECT count(*) as tt FROM OPINION")
            count_opiniones = cursor.fetchone()[0]

            cursor.execute("""
                    SELECT OP.OPINION, CL.RAZON_SOCIAL, AU.IMAGEN
                    FROM OPINION OP 
                    JOIN ORDEN_COMPRA OC ON OC.ID_ORDEN_DE_COMPRA = OP.ID_ORDEN_DE_COMPRA
                    JOIN CLIENTE CL ON OC.ID_CLIENTE = CL.ID_CLIENTE 
                    JOIN AUTH_USER AU ON CL.ID_USUARIO = AU.ID""")
            opiniones_db = cursor.fetchall()
            print(opiniones_db)

            if int(count_opiniones) > 3:
                opiniones = sample(opiniones_db, 3)
            else:
                opiniones = opiniones_db
                
            data["opiniones"] = opiniones
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