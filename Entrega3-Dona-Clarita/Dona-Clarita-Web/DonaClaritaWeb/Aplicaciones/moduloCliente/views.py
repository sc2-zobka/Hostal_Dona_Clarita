from django.shortcuts import render, redirect
from Aplicaciones.app.models import User, Huesped, ServicioAdicional, TipoComedor
from django.contrib import messages
from django.contrib import auth
from django.db import connection
from datetime import datetime, date
from django.contrib.auth.hashers import PBKDF2PasswordHasher
# Create your views here.


def dashboard_cli(request):
    huespedes = 0    
    orCompras = 0
    with connection.cursor() as cursor:
        try:
            cursor.execute("""SELECT COUNT(*) TT 
                              FROM APP_HUESPED H  
                              JOIN APP_CLIENTE C ON H.CLIENTE_ID = C.ID WHERE C.USUARIO_ID = %s""", [request.user.id])
            huespedes = cursor.fetchall()
            print(huespedes)
            cursor.execute("""SELECT COUNT(*) TT 
                              FROM APP_ORDENCOMPRA  OC
                              JOIN APP_CLIENTE C ON OC.CLIENTE_ID = C.ID
                              WHERE C.USUARIO_ID = %s""", [request.user.id])
            orCompras = cursor.fetchall()
            print(huespedes)            
                   
        except Exception as e:
            print(e)
            pass

    data = {
        'huespedes': huespedes,
        'orCompras':orCompras

        }
    return render(request, 'Clientes/dashboard.html', data)


def ordenes_compras(request):
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT ID FROM APP_CLIENTE WHERE USUARIO_ID = %s", [
                           request.user.id])
            cliente_db = cursor.fetchone()

            cursor.execute("SELECT OC.ID, OC.CANTIDAD_HUESPED, OC.MONTO_TOTAL, lower(DOC.DESCRIPCION), OC.ESTATUS_ORDEN_COMPRA_ID FROM APP_ORDENCOMPRA OC "
                           "JOIN APP_ESTATUSORDENCOMPRA DOC ON OC.ESTATUS_ORDEN_COMPRA_ID = DOC.ID WHERE CLIENTE_ID = %s", [cliente_db[0]])
            orden_compra_db = cursor.fetchall()

        except Exception as e:
            print(e)
            pass

    data = {
        'ordenes_compra': orden_compra_db
    }

    return render(request, 'Clientes/ordenes-compras.html', data)


def contarElementosLista(lista):
    """
    Recibe una lista, y devuelve un diccionario con todas las repeticiones de
    cada valor
    """
    return {i: lista.count(i) for i in lista}


def nueva_orden_compra(request):
    validaInfo = True  # Bloquea Formulario si perfil de cliente está incompleto
    bloquearCampos = True  # Bloquea Formulario si No tiene Trabajadores
    fdesde = ''  # Fecha Desde Formulario 1 (oc-form-1.html)
    fhasta = ''  # Fecha Hasta Formuario 1 (oc-form-1.html)
    nhuesped = ''  # Cantidad Alojamiento Formulario 1  (oc-form-1.html)
    servicio_ad = ''  # Servicios Adicionales Formulario 1 (oc-form-1.html)
    servicio_list = ''  # Servicios Adicionales Lista
    mensaje = ''  # Notifica Mensaje
    servicio_comedor = ''  # Servicio de Comedor Formulario 2(oc-form-2.html)
    servicio_comedor_list = ''  # Servicios de comedores, no se guardan valores null
    empleados_chk = ''  # Empleados a Alojar Formulario 2(oc-form-2.html)
    nrohabitaciones = ''  # Query Obtiene Habitaciones
    nroOC =''
    # Obtiene Habitación para empleado Formulario 3 (oc-form-3.html)
    nrohabitacion_list = ''
    capacidad = ''
    huespedes_list = ''  # Huespedes asociados al Cliente
    servicios_comedor_list = ''  # Tipos de comedores
    cantidad = '' #guarda Cantidad maxima de huespedes por habitaciones
   
    with connection.cursor() as cursor:
        try:
            #Consulta para Validar si Perfil está completo
            cursor.execute(f"""
            SELECT CL.RUT_EMPRESA, CL.DV, CL.DIRECCION, CL.COMUNA_ID 
            FROM APP_CLIENTE CL JOIN AUTH_USER US ON CL.USUARIO_ID = US.ID 
            WHERE US.USERNAME = '{request.user}'
            """)
            infoCliente = cursor.fetchone()
            validaInfo = True
            #Valida Perfil Completo (Campos Requeridos que no se guardan al crear)
            if infoCliente[0] and infoCliente[1] and infoCliente[2] and infoCliente[3]:
                validaInfo = False 
                #Consulta para Validar que Cliente Posea Trabajadores para alojar
                cursor.execute(f"""
                    SELECT COUNT(*)TT  
                    FROM APP_HUESPED HU
                    JOIN APP_CLIENTE CL ON HU.CLIENTE_ID = CL.ID
                    JOIN AUTH_USER US ON CL.USUARIO_ID = US.ID
                    WHERE US.USERNAME = '{request.user}'
                """)
                validaTrabajadores = cursor.fetchone()
                #Si no posee Se oculta el Formulario PASO 1
                if validaTrabajadores[0] < 1:
                    bloquearCampos = True
                    messages.warning(
                        request, 'No Posee Trabajadores, Cree o Cargue para poder continuar')
                else:
                    cursor.execute(
                        "SELECT ID, NOMBRE, PRECIO FROM APP_SERVICIOADICIONAL WHERE ESTADO = %s", [1])
                    servicios_adicionales_db = cursor.fetchall()
                    servicio_list = []

                    for servicio in servicios_adicionales_db:
                        servicio_m = ServicioAdicional()
                        servicio_m.id = servicio[0]
                        servicio_m.nombre = servicio[1]
                        servicio_m.precio = servicio[2]
                        servicio_list.append(servicio_m)
            else:
                #Alerta Perfil Incompleto y Oculta Formulario PASO 1
                validaInfo = True
                messages.warning(
                    request, 'Información incompleta, Termine de configurar para poder continuar ')

        except Exception as e:
            print(e)
            pass

    #Comprueba si Perfil está Completo
    if infoCliente[0] and infoCliente[1] and infoCliente[2] and infoCliente[3]:
        validaInfo = False
        #Comprueba si Cliente posee Trabajadores para alojar
        if validaTrabajadores[0] > 0:
            bloquearCampos = False
            # Se Valida si existe POST
            if request.method == "POST":
                # Fecha Desde Formulario 1 (oc-form-1.html) *** 1
                fdesde = request.POST['fdesde']
                # Fecha Hasta Formuario 1 (oc-form-1.html) ***1
                fhasta = request.POST['fhasta']
                # Cantidad Alojamiento Formulario 1  (oc-form-1.html)  ****1
                nhuesped = request.POST['nhuesped']
                try:
                    # Servicios Adicionales Formulario 1 (oc-form-1.html)
                    servicio_ad = request.POST.getlist('servicio_ad')
                except:
                    pass
                # Valida que traigan Datos Formulario 1 (oc-form-1.html)
                if len(fdesde) > 0 and len(fhasta) > 0 and len(nhuesped) > 0 and len(servicio_ad) >= 0:
                    # Valida fecha para que no sea mayor la de inicio a la de Termino (Desde - Hasta)
                    if (fdesde > fhasta):
                        mensaje = 'errorFecha'
                        messages.error(request, 'La Fecha de Desde No puede ser Mayor a la Fecha Hasta ')                        
                    else:                                            
                        if int(nhuesped) >= 1: # VALIDA QUE HUÉSPED SEA AL MENOS 1
                            if  validaTrabajadores[0] < int(nhuesped): # Valida que no pueda elegir más Huéspedes que trabajadores tenga
                                messages.error(request, 'La Cantidad de Huéspedes supera a sus trabajadores registrados')                                                                           
                            else:
                                         
                                with connection.cursor() as cursor:
                                    try:
                                        # QUERY PARA EXTRAER CANTIDAD DE HUÉSPEDES PERMITIDOS EN RANGO DE FECHA 
                                        cursor.execute(f"""
                                        SELECT sum(TH.CAPACIDAD)tt
                                            FROM APP_HABITACION H 
                                            join APP_TIPOHABITACION TH ON H.TIPO_HABITACION_ID = TH.ID
                                        WHERE H.ID NOT IN (
                                            SELECT HABITACION_ID 
                                                FROM APP_RESERVA R
                                                JOIN APP_DETALLEORDENCOMPRA DOC ON R.DETALLE_ORDEN_COMPRA_ID = DOC.ID
                                        WHERE INICIO_ESTADIA BETWEEN '{fdesde}' AND '{fhasta}' OR FINAL_ESTADIA BETWEEN '{fdesde}' AND '{fhasta}'   );
                                        """)     
                                                                             
                                        cantidad = cursor.fetchone() 
                                        if cantidad[0]:                                      
                                            if cantidad[0] < int(nhuesped):
                                                messages.error(request, f'El Número de Húespedes Supera el máximo de Habitaciones Disponibles. Cantidad Disponible {cantidad[0]}')
                                                return redirect('oc-new') 
                                        else:
                                            messages.error(request, f'No existe Disponibilidad de Habitaciones para el Periodo de Fecha Indicado')
                                            return redirect('oc-new') 
                                        print(cantidad[0])                                          
                                        print(fdesde)
                                        print(fhasta)
                                        # QUERY PARA EXTRAER HABITACIONES 
                                        cursor.execute(f"""
                                            SELECT h.numero_habitacion, h.id, h.descripcion, h.tipo_habitacion_id, th.descripcion, th.capacidad, h.precio
                                            FROM APP_HABITACION H 
                                            join APP_TIPOHABITACION TH ON H.TIPO_HABITACION_ID = TH.ID
                                            WHERE H.ID NOT IN (
                                                            SELECT HABITACION_ID 
                                            FROM APP_RESERVA R
                                            JOIN APP_DETALLEORDENCOMPRA DOC ON R.DETALLE_ORDEN_COMPRA_ID = DOC.ID
                                            WHERE INICIO_ESTADIA BETWEEN '{fdesde}' AND '{fhasta}' OR FINAL_ESTADIA BETWEEN '{fdesde}' AND '{fhasta}'   );
                                        """)
                                        nrohabitaciones = cursor.fetchall()
                                        if not nrohabitaciones:# VALIDA HABITACIONES DISPONIBLES EN RANGO DE FECHA
                                            messages.error(request, 'No existe Disponibilidad para el Periodo de Fecha Indicado')
                                            return redirect('oc-new')                                        
                                    except Exception as e:
                                        print(e)
                                        pass                            
                                with connection.cursor() as cursor:
                                    try:
                                        cursor.execute("SELECT ID FROM APP_CLIENTE WHERE USUARIO_ID = %s", [
                                                    request.user.id])
                                        cliente_db = cursor.fetchone()

                                        cursor.execute("SELECT ID, RUT, DV, NOMBRE, APELLIDO_P, APELLIDO_M FROM APP_HUESPED WHERE CLIENTE_ID = %s AND ESTADO = %s", [
                                                    cliente_db[0], 1])
                                        huespedes_db = cursor.fetchall()
                                        huespedes_list = []

                                        for huesped in huespedes_db:
                                            huesped_m = Huesped()
                                            huesped_m.id = huesped[0]
                                            huesped_m.rut = huesped[1]
                                            huesped_m.dv = huesped[2]
                                            huesped_m.nombre = huesped[3]
                                            huesped_m.apellido_p = huesped[4]
                                            huesped_m.apellido_m = huesped[5]

                                            huespedes_list.append(huesped_m)

                                        cursor.execute(
                                            "SELECT ID, DESCRIPCION FROM APP_TIPOCOMEDOR WHERE ESTADO = %s", [1])
                                        servicios_comedor_db = cursor.fetchall()
                                        servicios_comedor_list = []

                                        for servicio in servicios_comedor_db:
                                            servicio_m = TipoComedor()
                                            servicio_m.id = servicio[0]
                                            servicio_m.descripcion = servicio[1]

                                            servicios_comedor_list.append(
                                                servicio_m)

                                    except Exception as e:
                                        print(e)
                                        pass

                                # Mensaje Para pasar a segundo formulario (oc-form-2.html)
                                mensaje = 'sigue'
                                # Servicio de Comedor Formulario 2(oc-form-2.html)  []
                                servicio_comedor = request.POST.getlist('servicio')
                                # Empleados a Alojar Formulario 2(oc-form-2.html) []
                                empleados_chk = request.POST.getlist('chk')
                                servicio_comedor_list = []

                                for servicio in servicio_comedor:
                                    if servicio is not '':
                                        servicio_comedor_list.append(servicio)



                                # LEN PASO 2
                                # Valida que traigan Datos Formulario 2 (oc-form-2.html)
                                if len(servicio_comedor) > 0 and len(empleados_chk) > 0:
                                    mensaje = 'sigue2'

                                    nrohabitacion_list = request.POST.getlist(
                                        'nrohabitacion')

                                    with connection.cursor() as cursor:
                                        try:
                                            huespedes_list = []

                                            for trabajador_rut in empleados_chk:
                                                cursor.execute("SELECT ID, RUT, DV, NOMBRE, APELLIDO_P, APELLIDO_M FROM APP_HUESPED WHERE RUT = %s", [
                                                            trabajador_rut])
                                                huespedes_db = cursor.fetchone()

                                                huesped_m = Huesped()
                                                huesped_m.id = huespedes_db[0]
                                                huesped_m.rut = huespedes_db[1]
                                                huesped_m.dv = huespedes_db[2]
                                                huesped_m.nombre = huespedes_db[3]
                                                huesped_m.apellido_p = huespedes_db[4]
                                                huesped_m.apellido_m = huespedes_db[5]

                                                huespedes_list.append(huesped_m)
                                        except Exception as e:
                                            print(e)
                                            pass

                                    # Valida que traigan Datos Formulario 3 (oc-form-3.html)#[]
                                    if len(nrohabitacion_list) > 0:
                                        print(servicio_comedor)
                                        print(empleados_chk)
                                        lista = contarElementosLista(
                                            nrohabitacion_list)
                                        print(lista)
                                        for h, c in lista.items():
                                            print(h, c)
                                            with connection.cursor() as cursor:
                                                try:
                                                    cursor.execute("""
                                                                select h.id, h.numero_habitacion,th.capacidad, h.descripcion, h.tipo_habitacion_id, th.descripcion
                                                                from app_habitacion h
                                                                join app_tipohabitacion th ON h.tipo_habitacion_id = th.id
                                                                where h.numero_habitacion  = %s and th.capacidad >= %s
                                                        """, [h, c]
                                                    )
                                                    capacidad = cursor.fetchone()
                                                    if capacidad == None:
                                                        print('prueba 5')
                                                        mensaje = 'errorCapacidad'
                                                        messages.error(request, 'Excede el máximo permitido por Habitación')
                                                        break
                                                    else:
                                                        #
                                                        # SECCION ORDEN DE COMPRA
                                                        #

                                                        #
                                                        # Variables para calcular montos de la orden de compra
                                                        #
                                                        monto_servicio_adicional = 0
                                                        monto_comedor = 0
                                                        monto_habitacion = 0
                                                        monto_oc_total = 0
                                                        monto_oc_neto = 0
                                                        monto_iva = 0

                                                        #
                                                        # Obtener fecha de emision
                                                        #
                                                        fecha_emision_get = date.today()
                                                        fecha_emision = fecha_emision_get.strftime(
                                                            "%Y-%m-%d")

                                                        #
                                                        # Obtener ID de Cliente
                                                        #
                                                        cursor.execute("SELECT ID FROM APP_CLIENTE WHERE USUARIO_ID = %s", [
                                                                    request.user.id])
                                                        cliente_db = cursor.fetchone()

                                                        #
                                                        # Obtener ID Estatus Orden de compra 'Pendiente'
                                                        #
                                                        cursor.execute(
                                                            "SELECT ID FROM APP_ESTATUSORDENCOMPRA WHERE DESCRIPCION LIKE %s", ['pendiente'])
                                                        estatus_orden_compra = cursor.fetchone()

                                                        #
                                                        # Insertar registro de Orden de Compra inicial
                                                        #
                                                        cursor.execute("INSERT INTO APP_ORDENCOMPRA (FECHA_EMISION, CANTIDAD_HUESPED, "
                                                                    "CLIENTE_ID, ESTATUS_ORDEN_COMPRA_ID) VALUES (%s, %s, %s, %s)",
                                                                    [fecha_emision, nhuesped, cliente_db[0], estatus_orden_compra[0]])

                                                        #
                                                        # SECCION DETALLE ORDEN DE COMPRA
                                                        #

                                                        #
                                                        # Obtener ID de Orden de Compra anterior
                                                        #
                                                        cursor.execute(
                                                            "SELECT ID FROM APP_ORDENCOMPRA WHERE FECHA_EMISION = %s AND CLIENTE_ID = %s order by ID DESC", \
                                                                [fecha_emision, cliente_db[0]])
                                                        orden_compra_db = cursor.fetchone()

                                                        #
                                                        # Insertar registro de Detalle Orden de Compra inicial
                                                        #
                                                        cursor.execute("INSERT INTO APP_DETALLEORDENCOMPRA (INICIO_ESTADIA, FINAL_ESTADIA, "
                                                                    "ORDEN_COMPRA_ID) VALUES (%s, %s, %s)",
                                                                    [fdesde, fhasta, orden_compra_db[0]])

                                                        #
                                                        # SECCION RESERVA
                                                        #

                                                        #
                                                        # Obtener ID Detalle Orden de Compra anterior
                                                        #
                                                        cursor.execute("SELECT ID FROM APP_DETALLEORDENCOMPRA WHERE ORDEN_COMPRA_ID = %s",
                                                                    [orden_compra_db[0]])
                                                        detalle_orden_compra_db = cursor.fetchone()
                                                        for index in range(len(empleados_chk)):
                                                            #
                                                            # Obtener ID Huesped
                                                            #
                                                            cursor.execute("SELECT ID FROM APP_HUESPED WHERE RUT = %s", [
                                                                        empleados_chk[index]])
                                                            huesped_db = cursor.fetchone()

                                                            #
                                                            # Obtener ID Habitacion
                                                            #
                                                            cursor.execute("SELECT ID, PRECIO FROM APP_HABITACION WHERE NUMERO_HABITACION = %s",
                                                                        [nrohabitacion_list[index]])
                                                            habitacion_db = cursor.fetchone()
                                                            monto_habitacion = monto_habitacion + int(habitacion_db[1])

                                                            #
                                                            # Obtener ID Tipo Comedor
                                                            #
                                                            cursor.execute("SELECT ID, PRECIO FROM APP_TIPOCOMEDOR WHERE ID = %s",
                                                                        [servicio_comedor_list[index]])
                                                            tipo_comedor_db = cursor.fetchone()
                                                            monto_comedor = monto_comedor + int(tipo_comedor_db[1])

                                                            #
                                                            # Insertar registro de Reserva
                                                            #
                                                            cursor.execute("INSERT INTO APP_RESERVA (CHECK_IN, DETALLE_ORDEN_COMPRA_ID, "
                                                                        "HABITACION_ID, HUESPED_ID, TIPO_COMEDOR_ID) VALUES (%s, %s, %s, %s, %s)",
                                                                        [0, detalle_orden_compra_db[0], habitacion_db[0], huesped_db[0], tipo_comedor_db[0]])
                                                            cursor.execute("""SELECT OC.ID 
                                                                            FROM APP_ORDENCOMPRA  OC
                                                                            JOIN APP_CLIENTE C ON OC.CLIENTE_ID = C.ID
                                                                            WHERE C.USUARIO_ID = %s ORDER BY OC.ID DESC LIMIT 1""", [request.user.id])

                                                            nroOC = cursor.fetchone() #almacena número de Orden de Compra realizada
                                                            print('orden de compra n°',nroOC)

                                                        #
                                                        # Actualizar monto de la orden de compra
                                                        #
                                                        
                                                        #
                                                        # Leer servicios adicionales
                                                        #
                                                        if len(servicio_ad) > 0:
                                                            for servicio_adicional in servicio_ad:
                                                                #
                                                                # Obtener Servicio adicional
                                                                #
                                                                cursor.execute("SELECT ID, PRECIO FROM APP_SERVICIOADICIONAL WHERE ID = %s",
                                                                            [servicio_adicional])
                                                                serv_adic_db = cursor.fetchone()
                                                                monto_servicio_adicional = monto_servicio_adicional + int(serv_adic_db[1])

                                                                #
                                                                # Insertar Detalle Servicio Adicional
                                                                #
                                                                cursor.execute("INSERT INTO APP_DETALLESERVICIOADICIONAL (DETALLE_ORDEN_COMPRA_ID, SERVICIO_ADICIONAL_ID) " \
                                                                    "VALUES (%s, %s)", [detalle_orden_compra_db[0], serv_adic_db[0]])
                                                        
                                                        monto_servicio_adicional = (monto_servicio_adicional * len(empleados_chk))
                                                        monto_oc_total = (monto_servicio_adicional + monto_comedor + monto_habitacion)

                                                        monto_iva = round(monto_oc_total * 0.19)
                                                        monto_oc_neto = monto_oc_total
                                                        monto_oc_total = monto_oc_total + monto_iva

                                                        cursor.execute("UPDATE APP_ORDENCOMPRA SET MONTO_TOTAL = %s, MONTO_NETO = %s, IVA = %s WHERE ID = %s",
                                                            [monto_oc_total, monto_oc_neto, monto_iva, orden_compra_db[0]])

                                                        messages.success(request, f'Se ha realizado la Orden de Compra N° {nroOC[0]} de Manera Correcta')
                                                        return redirect('oc-list')
                                                except Exception as e:
                                                    print(e)
                                                    messages.error(request, 'Ocurrió un problema mientras se ejecutaba, Revise Try de Extracción de Datos')
                                    else:
                                        # Al no encontrar variable en POST se cae y se manda a Formulario Correspondiente (oc-form-3.html)
                                        mensaje = 'sigue2'
                                else:
                                    # Al no encontrar variable en POST se cae y se manda a Formulario Correspondiente (oc-form-2.html)
                                    mensaje = 'sigue'
                        else:
                            messages.error(request, 'La Fecha de Desde No puede ser Mayor a la Fecha Hasta ')  # Mensaje Cuando Huésped es menor a 1
                else:
                    print('prueba 1')
                    # Encuentra error en Primer POST (oc-form-1.html)
                    mensaje = 'error'
    data = {
        'mensaje': mensaje,
        'fdesde': fdesde,
        'fhasta': fhasta,
        'nhuesped': nhuesped,
        'servicio_ad': servicio_ad,
        'nrohabitaciones': nrohabitaciones,
        'servicio_comedor': servicio_comedor,
        'empleados_chk': empleados_chk,
        'servicios_list': servicio_list,
        'inicio_index': 0,
        'trabajadores': huespedes_list,
        'comedores': servicios_comedor_list,
        'bloquearCampos': bloquearCampos,
        'validaInfo': validaInfo,
        'nroOC':nroOC
    }

    return render(request, 'Clientes/ordenes-compra-new.html', data)


def facturas_cli(request):
    return render(request, 'Clientes/facturas.html')


def det_factura_cli(request):
    return render(request, 'Clientes/det-factura.html')


def factura_print(request):
    return render(request, 'Clientes/factura.html')


# --------------------------FIN CLIENTES
