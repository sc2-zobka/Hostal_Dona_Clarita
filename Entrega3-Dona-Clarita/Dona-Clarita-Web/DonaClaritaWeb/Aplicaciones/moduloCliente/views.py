from Aplicaciones.moduloEmpleado.views import documentos, print_pedidos
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
    cant_doc = 0
    gastos = 0
    op_pendientes = 0
    op_totales = 0
    total_facturas = 0
    total_notacredito = 0
    with connection.cursor() as cursor:
        try:
            if request.user.is_cliente:
                cursor.execute("""SELECT COUNT(*) TT 
                                FROM HUESPED H  
                                JOIN CLIENTE C ON H.ID_CLIENTE = C.ID_CLIENTE WHERE C.ID_USUARIO = %s""", [request.user.id])
                huespedes = cursor.fetchall()
                print(huespedes)
                cursor.execute("""SELECT COUNT(*) TT 
                                FROM ORDEN_COMPRA  OC
                                JOIN CLIENTE C ON OC.ID_CLIENTE = C.ID_CLIENTE
                                WHERE C.ID_USUARIO = %s""", [request.user.id])
                orCompras = cursor.fetchall()
                print(huespedes)            
                cursor.execute(f"""
                SELECT COUNT(D.ID_DOCUMENTO)TT
                FROM ORDEN_COMPRA OC
                JOIN CLIENTE C ON OC.ID_CLIENTE = C.ID_CLIENTE
                JOIN DOCUMENTO D ON OC.ID_ORDEN_DE_COMPRA = D.ID_ORDEN_DE_COMPRA
                WHERE C.ID_USUARIO = {request.user.id}
                """)       
                cant_doc = cursor.fetchone()[0]
                cursor.execute(f"""
                SELECT SUM(D.MONTO_TOTAL)TT
                FROM ORDEN_COMPRA OC
                JOIN CLIENTE C ON OC.ID_CLIENTE = C.ID_CLIENTE
                JOIN DOCUMENTO D ON OC.ID_ORDEN_DE_COMPRA = D.ID_ORDEN_DE_COMPRA
                WHERE C.ID_USUARIO = {request.user.id} AND D.CODIGO_SII = 33
                """)
                total_facturas = cursor.fetchone()[0]
                cursor.execute(f"""
                SELECT SUM(D.MONTO_TOTAL)TT
                FROM ORDEN_COMPRA OC
                JOIN CLIENTE C ON OC.ID_CLIENTE = C.ID_CLIENTE
                JOIN DOCUMENTO D ON OC.ID_ORDEN_DE_COMPRA = D.ID_ORDEN_DE_COMPRA
                WHERE C.ID_USUARIO = {request.user.id} AND D.CODIGO_SII = 61
                """)
                total_notacredito = cursor.fetchone()[0]            

                gastos = total_facturas-total_notacredito
            if request.user.is_proveedor:
                cursor.execute(f"""
                SELECT COUNT(*)TT
                    FROM ORDEN_PEDIDO OP
                    JOIN ESTATUS_ORDEN_PEDIDO EOP ON OP.ID_ESTATUS_ORDEN_PEDIDO = EOP.ID_ESTATUS_ORDEN_PEDIDO
                    JOIN CLIENTE C ON OP.ID_CLIENTE = C.ID_CLIENTE
                    JOIN AUTH_USER AU ON C.ID_USUARIO = AU.ID
                    WHERE EOP.DESCRIPCION = 'ENVIADA' AND AU.ID = {request.user.id}
                """)
                op_pendientes = cursor.fetchone()[0]
                cursor.execute(f"""
                SELECT COUNT(*)TT
                    FROM ORDEN_PEDIDO OP
                    JOIN ESTATUS_ORDEN_PEDIDO EOP ON OP.ID_ESTATUS_ORDEN_PEDIDO = EOP.ID_ESTATUS_ORDEN_PEDIDO
                    JOIN CLIENTE C ON OP.ID_CLIENTE = C.ID_CLIENTE
                    JOIN AUTH_USER AU ON C.ID_USUARIO = AU.ID
                    WHERE AU.ID = {request.user.id}
                """)
                op_totales = cursor.fetchone()[0]

        except Exception as e:
            print(e)
            pass

    data = {
        'huespedes': huespedes,
        'orCompras':orCompras,
        'cant_doc':cant_doc,
        'gastos':gastos,
        'total_facturas':total_facturas,
        'total_notacredito':total_notacredito,
        'op_pendientes':op_pendientes,
        'op_totales':op_totales

        }
    return render(request, 'Clientes/dashboard.html', data)


def ordenes_compras(request):
    orden_compra_db = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT ID_CLIENTE FROM CLIENTE WHERE ID_USUARIO = %s", [
                           request.user.id])
            cliente_db = cursor.fetchone()
            print(cliente_db)
            cursor.execute("SELECT OC.ID_ORDEN_DE_COMPRA, OC.CANT_HUESPED, OC.MONTO_TOTAL, lower(DOC.DESCRIPCION), OC.ID_ESTATUS_ORDEN_COMPRA FROM ORDEN_COMPRA OC "
                           "JOIN ESTATUS_ORDEN_COMPRA DOC ON OC.ID_ESTATUS_ORDEN_COMPRA = DOC.ID_ESTATUS_ORDEN_COMPRA WHERE ID_CLIENTE = %s", [cliente_db[0]])
            orden_compra_db = cursor.fetchall()

        except Exception as e:
            print(e)
            pass

    data = {
        'ordenes_compra': orden_compra_db
    }

    return render(request, 'Clientes/ordenes-compras.html', data)

def print_orden_compra(request,id):
    datos_empresa = ''
    idUS = ''
    idCliente = ''
    cabecera_oc = ''
    nroOC = ''
    serv_ad = ''
    habitaciones = ''
    detcomedor = ''
    with connection.cursor() as cursor:
        try:
            #CONDICIONAL PARA DIFERENCIAR CLIENTE U OTRO
            if request.user.is_cliente:
                #SE TOMA ID DEL USUARIO
                idUS = request.user.id
                cursor.execute(f""" SELECT OC.ID_CLIENTE 
                FROM ORDEN_COMPRA OC
                JOIN CLIENTE C ON OC.ID_CLIENTE = C.ID_CLIENTE
                JOIN AUTH_USER AU ON C.ID_USUARIO = AU.ID
                WHERE AU.ID = {idUS} AND OC.ID_ORDEN_DE_COMPRA ={id}
                            """)
                #SE EXTRAE ID CLIENTE PARA CONSULTAR LUEGO
                idCliente = cursor.fetchone()[0]
            else:
                #QWERY QUE EXTRAE ID CLIENTE DESDE ORDEN DE COMPRA CUANDO EL USUARIO NO ES UN CLIENTE
                cursor.execute(f""" SELECT OC.ID_CLIENTE 
                FROM ORDEN_COMPRA OC
                WHERE OC.ID_ORDEN_DE_COMPRA ={id}
                            """)
                #SE EXTRAE ID CLIENTE PARA CONSULTAR LUEGO            
                idCliente = cursor.fetchone()[0]
            #QWERY PARA EXTRAER DATOS DEL CLIENTE Y ORDEN DE COMPRA PARA CABECERA DE IMPRESIÓN
            cursor.execute(f"""
                SELECT  OC.ID_ORDEN_DE_COMPRA AS "0 OC",C.ID_CLIENTE AS "1 ID_CLI", UPPER(C.RAZON_SOCIAL) AS "2 RS", 
                C.RUT_EMPRESA AS "3 RUT", C.DV AS "4 DV",
                UPPER( C.DIRECCION||', '||CO.DESCRIPCION ) AS "5 DIR",
                NVL(OC.MONTO_NETO,0) AS "6 NETO", NVL(OC.IVA,0) AS "7 IVA", NVL(OC.MONTO_TOTAL,0) AS "8 TT",UPPER(EOC.DESCRIPCION) AS "9 ESTADO",
                TO_CHAR(OC.FECHA_EMISION, 'DD-MM-YYYY') AS "10 FEC EM"
                FROM ORDEN_COMPRA OC 
                JOIN CLIENTE C ON OC.ID_CLIENTE = C.ID_CLIENTE 
                JOIN COMUNA CO ON C.COMUNA_ID = CO.COMUNA_ID
                JOIN ESTATUS_ORDEN_COMPRA EOC ON OC.ID_ESTATUS_ORDEN_COMPRA = EOC.ID_ESTATUS_ORDEN_COMPRA 
                WHERE OC.ID_ORDEN_DE_COMPRA = {id} AND OC.ID_CLIENTE = {idCliente}
            """)
            cabecera_oc = cursor.fetchone()
            #QWERY QUE EXTRAE DATOS DE LA EMPRESA DESDE CONFIGURACIÓN (HOSTAL DOÑA CLARITA) PARA DATOS GENERALES DE LA IMPRESIÓN
            cursor.execute("""
               SELECT UPPER(C.NOMBRE_EMPRESA) AS "0 RS", UPPER(C.DIRECCION) AS "1 DIR", CO.DESCRIPCION AS "2 COM", 
                UPPER(REPLACE(REPLACE(REPLACE(R.DESCRIPCION,'Región del',''), 'Región de',''), 'Región Metropolitana de','')) AS "3 REG",
                E.CELULAR AS "4 CEL", UPPER(US.EMAIL) AS "5 EMAIL", C.LOGO_EMPRESA AS "6 LOGO", C.RUT_EMPRESA AS "7", C.DV AS "8"
                FROM CONFIGURACION C
                JOIN COMUNA CO ON C.COMUNA_ID = CO.COMUNA_ID
                JOIN REGION R ON CO.ID_REGION = R.ID_REGION
                JOIN EMPLEADO E ON C.ID_USUARIO = E.ID_USUARIO
                JOIN AUTH_USER US ON C.ID_USUARIO = US.ID     
            """)
            datos_empresa = cursor.fetchone() 
            nroOC = cabecera_oc[0]
            #/*SACA SERVICIOS ADICIONALES */
            cursor.execute(f"""
                SELECT COUNT(*)AS TT,DOC.ID_ORDEN_DE_COMPRA, SA.NOMBRE, ROUND(SUM(SA.PRECIO)/COUNT(*),2) AS UNITARIO, SUM(SA.PRECIO) AS TOTAL
                FROM DETALLE_ORDEN_COMPRA DOC
                LEFT JOIN DETALLE_SERVICIO_ADICIONAL DSA ON DOC.ID_DETALLE_ORDEN_DE_COMPRA = DSA.ID_DETALLE_ORDEN_DE_COMPRA
                LEFT JOIN SERVICIO_ADICIONAL SA ON DSA.ID_SERVICIO = SA.ID_SERVICIO
                WHERE DOC.ID_ORDEN_DE_COMPRA = {nroOC} /*VARIABLE 12*/
                GROUP BY DOC.ID_ORDEN_DE_COMPRA, SA.NOMBRE, SA.PRECIO
            """)
            serv_ad = cursor.fetchall()
            if serv_ad[0][2] is None:
                serv_ad = ''
            #/*SACA CANTIDAD Y RESUMEN DE COMEDORES */
            cursor.execute(f"""                
                SELECT  COUNT(*) AS "0 CANT", ('Servicio de Comedor Tipo:'||' '|| (TC.DESCRIPCION)) AS "1 DES", ROUND(SUM(TC.PRECIO)/COUNT(*),2)AS "2 UNITARIO", SUM(TC.PRECIO) AS "3 TOTAL"
                FROM DETALLE_ORDEN_COMPRA DOC
                JOIN RESERVA R ON DOC.ID_DETALLE_ORDEN_DE_COMPRA = R.ID_DETALLE_ORDEN_DE_COMPRA
                JOIN TIPO_COMEDOR TC ON R.ID_TIPO_COMEDOR = TC.ID_TIPO_COMEDOR
                WHERE DOC.ID_ORDEN_DE_COMPRA = {nroOC} 
                GROUP BY TC.DESCRIPCION, TC.PRECIO
            """)
            detcomedor = cursor.fetchall()
            #/*SACA CANTIDAD Y RESUMEN DE HABITACIONES */
            cursor.execute(f"""
                SELECT  COUNT(*) AS "0 TT", ('Habitación' ||' '||TH.DESCRIPCION ||' Pieza N° '||H.NUMERO_HABITACION ) AS "1 DESCRIPCION", 
                ROUND(SUM(H.PRECIO)/COUNT(*),2) AS "2 UNITARIO", SUM(H.PRECIO) AS "3 TOTAL"
                FROM DETALLE_ORDEN_COMPRA DOC
                JOIN RESERVA R ON DOC.ID_DETALLE_ORDEN_DE_COMPRA = R.ID_DETALLE_ORDEN_DE_COMPRA
                JOIN HABITACION H ON R.ID_HABITACION  = H.ID_HABITACION
                JOIN TIPO_HABITACION TH ON H.ID_TIPO_HABITACION = TH.ID_TIPO_HABITACION
                WHERE DOC.ID_ORDEN_DE_COMPRA = {nroOC} 
                GROUP BY ('Habitación' ||' '||TH.DESCRIPCION ||' Pieza N° '||H.NUMERO_HABITACION ), H.PRECIO
            """)
            habitaciones = cursor.fetchall()                   
        except Exception as e:
            print(e)
            pass

    data = {
        'datos_empresa': datos_empresa,
        'cabecera_oc':cabecera_oc,
        'serv_ad':serv_ad,
        'detcomedor':detcomedor,
        'habitaciones':habitaciones
        }
    return render(request, 'Clientes/OrdenCompra/print_ordenCompra.html', data)

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
    validaTrabajadores = '' #Valida existencia de trabajadores para pasar a paso 2
    with connection.cursor() as cursor:
        try:
            #Consulta para Validar si Perfil está completo
            cursor.execute(f"""
            SELECT CL.RUT_EMPRESA, CL.DV, CL.DIRECCION, CL.COMUNA_ID 
            FROM CLIENTE CL JOIN AUTH_USER US ON CL.ID_USUARIO = US.ID 
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
                    FROM HUESPED HU
                    JOIN CLIENTE CL ON HU.ID_CLIENTE = CL.ID_CLIENTE
                    JOIN AUTH_USER US ON CL.ID_USUARIO = US.ID
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
                        "SELECT ID_SERVICIO, NOMBRE, PRECIO FROM SERVICIO_ADICIONAL WHERE ESTADO = %s", [1])
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
                                        print(f"""
                                        SELECT sum(TH.CAPACIDAD)tt
                                            FROM HABITACION H 
                                            join TIPO_HABITACION TH ON H.ID_TIPO_HABITACION = TH.ID_TIPO_HABITACION
                                        WHERE H.ID_TIPO_HABITACION NOT IN (
                                            SELECT ID_HABITACION 
                                                FROM RESERVA R
                                                JOIN DETALLE_ORDEN_COMPRA DOC ON R.ID_DETALLE_ORDEN_DE_COMPRA = DOC.ID_DETALLE_ORDEN_DE_COMPRA
                                        WHERE INICIO_ESTADIA BETWEEN '{fdesde}' AND '{fhasta}' OR FINAL_ESTADIA BETWEEN '{fdesde}' AND '{fhasta}'   );
                                        """) 
                                        cursor.execute(f"""
                                        SELECT sum(TH.CAPACIDAD)tt
                                            FROM HABITACION H 
                                            join TIPO_HABITACION TH ON H.ID_TIPO_HABITACION = TH.ID_TIPO_HABITACION
                                        WHERE H.ID_HABITACION NOT IN (
                                            SELECT ID_HABITACION 
                                                FROM RESERVA R
                                                JOIN DETALLE_ORDEN_COMPRA DOC ON R.ID_DETALLE_ORDEN_DE_COMPRA = DOC.ID_DETALLE_ORDEN_DE_COMPRA
                                        WHERE INICIO_ESTADIA BETWEEN '{fdesde}' AND '{fhasta}' OR FINAL_ESTADIA BETWEEN '{fdesde}' AND '{fhasta}'   )
                                        """)     
                                        print('asigno cantidad')                            
                                        cantidad = cursor.fetchone() 
                                        print(cantidad[0]) 
                                        if cantidad[0]:                                      
                                            if cantidad[0] < int(nhuesped):
                                                messages.error(request, f'El Número de Húespedes Supera el máximo de Habitaciones Disponibles. Cantidad Disponible {cantidad[0]}')
                                                return redirect('oc-new') 
                                        else:
                                            messages.error(request, f'No existe Disponibilidad de Habitaciones para el Periodo de Fecha Indicado')
                                            return redirect('oc-new') 
                                                                                 
                                        print(fdesde)
                                        print(fhasta)
                                        # QUERY PARA EXTRAER HABITACIONES 
                                        cursor.execute(f"""
                                            SELECT h.numero_habitacion, h.ID_HABITACION, h.descripcion, h.ID_TIPO_HABITACION, th.descripcion, th.capacidad, h.precio
                                            FROM HABITACION H 
                                            join TIPO_HABITACION TH ON H.ID_TIPO_HABITACION = TH.ID_TIPO_HABITACION
                                            WHERE H.ID_HABITACION NOT IN (
                                                            SELECT ID_HABITACION 
                                            FROM RESERVA R
                                            JOIN DETALLE_ORDEN_COMPRA DOC ON R.ID_DETALLE_ORDEN_DE_COMPRA = DOC.ID_DETALLE_ORDEN_DE_COMPRA
                                            WHERE INICIO_ESTADIA BETWEEN '{fdesde}' AND '{fhasta}' OR FINAL_ESTADIA BETWEEN '{fdesde}' AND '{fhasta}'   )
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
                                        cursor.execute("SELECT ID_CLIENTE FROM CLIENTE WHERE ID_USUARIO = %s", [
                                                    request.user.id])
                                        cliente_db = cursor.fetchone()

                                        cursor.execute("SELECT ID_HUESPED, RUT, DV, NOMBRE, APELLIDO_P, APELLIDO_M FROM HUESPED WHERE ID_CLIENTE = %s AND ESTADO = %s", [
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
                                            "SELECT ID_TIPO_COMEDOR, DESCRIPCION FROM TIPO_COMEDOR WHERE ESTADO = %s", [1])
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
                                    if servicio != '':
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
                                                cursor.execute("SELECT ID_HUESPED, RUT, DV, NOMBRE, APELLIDO_P, APELLIDO_M FROM HUESPED WHERE RUT = %s", [
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
                                        print('imprime lista',lista)
                                        for h, c in lista.items():
                                            print(h, c)
                                            with connection.cursor() as cursor:
                                                try:
                                                    cursor.execute("""
                                                                select h.id_habitacion, h.numero_habitacion,th.capacidad, h.descripcion, h.id_tipo_habitacion, th.descripcion
                                                                from habitacion h
                                                                join tipo_habitacion th ON h.id_tipo_habitacion = th.id_tipo_habitacion
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
                                                            "%d-%m-%Y")

                                                        #
                                                        # Obtener ID de Cliente
                                                        #
                                                        cursor.execute("SELECT ID_CLIENTE FROM CLIENTE WHERE ID_USUARIO = %s", [
                                                                    request.user.id])
                                                        cliente_db = cursor.fetchone()

                                                        #
                                                        # Obtener ID Estatus Orden de compra 'Pendiente'
                                                        #
                                                        cursor.execute(
                                                            "SELECT ID_ESTATUS_ORDEN_COMPRA FROM ESTATUS_ORDEN_COMPRA WHERE DESCRIPCION LIKE %s", ['Pendiente'])
                                                        estatus_orden_compra = cursor.fetchone()
                                                        print("SELECT ID_ESTATUS_ORDEN_COMPRA FROM ESTATUS_ORDEN_COMPRA WHERE DESCRIPCION LIKE %s", ['Pendiente'])
                                                        
                                                        #
                                                        # Insertar registro de Orden de Compra inicial
                                                        #
                                                        cursor.execute("INSERT INTO ORDEN_COMPRA (FECHA_EMISION, CANT_HUESPED, "
                                                                    "ID_CLIENTE, ID_ESTATUS_ORDEN_COMPRA) VALUES (%s, %s, %s, %s)",
                                                                    [fecha_emision, nhuesped, cliente_db[0], estatus_orden_compra[0]])

                                                        #
                                                        # SECCION DETALLE ORDEN DE COMPRA
                                                        #

                                                        #
                                                        # Obtener ID de Orden de Compra anterior
                                                        #
                                                        print('id-oc')
                                                        cursor.execute(
                                                            "SELECT ID_ORDEN_DE_COMPRA FROM ORDEN_COMPRA WHERE FECHA_EMISION = %s AND ID_CLIENTE = %s order by ID_ORDEN_DE_COMPRA DESC", \
                                                                [fecha_emision, cliente_db[0]])
                                                        orden_compra_db = cursor.fetchone()
                                                        print("SELECT ID_ORDEN_DE_COMPRA FROM ORDEN_COMPRA WHERE FECHA_EMISION = %s AND ID_CLIENTE = %s order by ID_ORDEN_DE_COMPRA DESC", \
                                                                [fecha_emision, cliente_db[0]])
                                                        #
                                                        # Insertar registro de Detalle Orden de Compra inicial
                                                        #
                                                        print('insert det-oc')
                                                        cursor.execute("INSERT INTO DETALLE_ORDEN_COMPRA (INICIO_ESTADIA, FINAL_ESTADIA, "
                                                                    "ID_ORDEN_DE_COMPRA) VALUES (%s, %s, %s)",
                                                                    [fdesde, fhasta, orden_compra_db[0]])

                                                        #
                                                        # SECCION RESERVA
                                                        #

                                                        #
                                                        # Obtener ID Detalle Orden de Compra anterior
                                                        #
                                                        print('detalle-oc')
                                                        cursor.execute("SELECT ID_DETALLE_ORDEN_DE_COMPRA FROM DETALLE_ORDEN_COMPRA WHERE ID_ORDEN_DE_COMPRA = %s",
                                                                    [orden_compra_db[0]])
                                                        detalle_orden_compra_db = cursor.fetchone()
                                                        for index in range(len(empleados_chk)):
                                                            #
                                                            # Obtener ID Huesped
                                                            #
                                                            print('id-huesped')
                                                            cursor.execute("SELECT ID_HUESPED FROM HUESPED WHERE RUT = %s", [
                                                                        empleados_chk[index]])
                                                            huesped_db = cursor.fetchone()

                                                            #
                                                            # Obtener ID Habitacion
                                                            #
                                                            print('id-habtacion')
                                                            cursor.execute("SELECT ID_HABITACION, PRECIO FROM HABITACION WHERE NUMERO_HABITACION = %s",
                                                                        [nrohabitacion_list[index]])
                                                            habitacion_db = cursor.fetchone()
                                                            monto_habitacion = monto_habitacion + int(habitacion_db[1])

                                                            #
                                                            # Obtener ID Tipo Comedor
                                                            #
                                                            print('id-comedor')
                                                            cursor.execute("SELECT ID_TIPO_COMEDOR, PRECIO FROM TIPO_COMEDOR WHERE ID_TIPO_COMEDOR = %s",
                                                                        [servicio_comedor_list[index]])
                                                            tipo_comedor_db = cursor.fetchone()
                                                            monto_comedor = monto_comedor + int(tipo_comedor_db[1])

                                                            #
                                                            # Insertar registro de Reserva
                                                            #
                                                            print('insert reserva')
                                                            cursor.execute("INSERT INTO RESERVA (CHECK_IN, ID_DETALLE_ORDEN_DE_COMPRA, "
                                                                        "ID_HABITACION, ID_HUESPED, ID_TIPO_COMEDOR) VALUES (%s, %s, %s, %s, %s)",
                                                                        [0, detalle_orden_compra_db[0], habitacion_db[0], huesped_db[0], tipo_comedor_db[0]])
                                                                                                                                    
                                                            cursor.execute("""SELECT OC.ID_ORDEN_DE_COMPRA 
                                                                            FROM ORDEN_COMPRA  OC
                                                                            JOIN CLIENTE C ON OC.ID_CLIENTE = C.ID_CLIENTE
                                                                            WHERE C.ID_USUARIO = %s ORDER BY OC.ID_ORDEN_DE_COMPRA DESC""", [request.user.id])

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
                                                                cursor.execute("SELECT ID_SERVICIO, PRECIO FROM SERVICIO_ADICIONAL WHERE ID_SERVICIO = %s",
                                                                            [servicio_adicional])
                                                                serv_adic_db = cursor.fetchone()
                                                                monto_servicio_adicional = monto_servicio_adicional + int(serv_adic_db[1])

                                                                #
                                                                # Insertar Detalle Servicio Adicional
                                                                #
                                                                cursor.execute("INSERT INTO DETALLE_SERVICIO_ADICIONAL (ID_DETALLE_ORDEN_DE_COMPRA, ID_SERVICIO) " \
                                                                    "VALUES (%s, %s)", [detalle_orden_compra_db[0], serv_adic_db[0]])
                                                        
                                                        monto_servicio_adicional = (monto_servicio_adicional * len(empleados_chk))
                                                        monto_oc_total = (monto_servicio_adicional + monto_comedor + monto_habitacion)

                                                        monto_iva = round(monto_oc_total * 0.19)
                                                        monto_oc_neto = monto_oc_total
                                                        monto_oc_total = monto_oc_total + monto_iva

                                                        cursor.execute("UPDATE ORDEN_COMPRA SET MONTO_TOTAL = %s, MONTO_NETO = %s, IVA = %s WHERE ID_ORDEN_DE_COMPRA = %s",
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

    docs = ''
    idUs = request.user.id        
    print(idUs)    
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"""SELECT C.ID_CLIENTE 
                           FROM CLIENTE C
                           JOIN AUTH_USER AU ON C.ID_USUARIO = AU.ID
                           WHERE AU.ID = {idUs}
                           """)
            idCliente = cursor.fetchone()[0]
            print(idCliente)
            cursor.execute(f"""
                SELECT D.ID_DOCUMENTO AS "0 DOC", TD.ABREVIADO AS "1",NVL(OC.ID_ORDEN_DE_COMPRA,0) AS "2 OC",
                D.FECHA_EMISION AS "3", D.MONTO_TOTAL AS "4" , ED.ID_ESTATUS_DOCUMENTO AS "5",
                ED.DESCRIPCION AS "6"
                FROM DOCUMENTO D
                JOIN TIPO_DOCUMENTO TD ON D.CODIGO_SII = TD.CODIGO_SII
                LEFT JOIN ORDEN_COMPRA OC ON D.ID_ORDEN_DE_COMPRA = OC.ID_ORDEN_DE_COMPRA
                LEFT JOIN ORDEN_PEDIDO OP ON D.ID_ORDEN_PEDIDO = OP.ID_ORDEN_PEDIDO
                JOIN CLIENTE CL ON OC.ID_CLIENTE = CL.ID_CLIENTE
                JOIN ESTATUS_DOCUMENTO ED ON D.ID_ESTATUS_DOCUMENTO = ED.ID_ESTATUS_DOCUMENTO
                WHERE CL.ID_CLIENTE = {idCliente}
                          """)
            docs = cursor.fetchall()

        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            pass

    data = {
        'docs': docs,
     
    }    
    return render(request, 'Clientes/facturas.html',data)


def factura_print(request, id):
    documento = ''
    doc_total = ''
    serv_ad = ''
    detcomedor = ''
    habitaciones = ''
    datos_empresa = ''
    with connection.cursor() as cursor:
        try:
            #OBTENER CABECERA DE DOCUMENTO
            cursor.execute(f"""            
            SELECT CL.ID_CLIENTE AS "0", ( (CL.RUT_EMPRESA)) AS "1RUT",  UPPER(CL.RAZON_SOCIAL) AS "2",
                'COMERCIALIZACION DE PRODUCTOS' AS "3", TO_CHAR(D.FECHA_EMISION,'DD-MM-YYYY') AS "4",   UPPER(CL.DIRECCION) AS "5", CO.DESCRIPCION AS "6",
                TO_CHAR(D.FECHA_EMISION,'DD-MM-YYYY') AS "7", 'EFECTIVO / TRANSFERENCIA' AS "8", TD.ABREVIADO AS "9",  UPPER(TD.DESCRIPCION) AS "10", D.ID_DOCUMENTO AS "11DOC", 
                OC.ID_ORDEN_DE_COMPRA AS "12OC",  UPPER(ED.DESCRIPCION) AS "13", D.DOC_ANULADO AS "14ESTADO", CL.DV AS "15"
            FROM CLIENTE CL
            JOIN COMUNA CO ON CL.COMUNA_ID = CO.COMUNA_ID
            JOIN ORDEN_COMPRA OC ON CL.ID_CLIENTE = OC.ID_CLIENTE
            JOIN DOCUMENTO D ON OC.ID_ORDEN_DE_COMPRA = D.ID_ORDEN_DE_COMPRA
            JOIN TIPO_DOCUMENTO TD ON D.CODIGO_SII = TD.CODIGO_SII
            JOIN ESTATUS_DOCUMENTO ED ON D.ID_ESTATUS_DOCUMENTO = ED.ID_ESTATUS_DOCUMENTO
                WHERE ID_TIPO_CLIENTE = 1 AND D.ID_DOCUMENTO = {id}
            """)
            documento = cursor.fetchone()
            if not documento:
                messages.error(request, 'Documento Buscado NO Existe o fue Elimimado')
                if request.user.is_cliente:
                    return redirect('facturas-cli')
                else:
                    return redirect('ventas')
            else:
                cursor.execute("""
                    SELECT UPPER(C.NOMBRE_EMPRESA) AS "0 RS", UPPER(C.DIRECCION) AS "1 DIR", CO.DESCRIPCION AS "2 COM", 
                    UPPER(REPLACE(REPLACE(REPLACE(R.DESCRIPCION,'Región del',''), 'Región de',''), 'Región Metropolitana de','')) AS "3 REG",
                    E.CELULAR AS "4 CEL", UPPER(US.EMAIL) AS "5 EMAIL", C.LOGO_EMPRESA AS "6 LOGO"
                    FROM CONFIGURACION C
                    JOIN COMUNA CO ON C.COMUNA_ID = CO.COMUNA_ID
                    JOIN REGION R ON CO.ID_REGION = R.ID_REGION
                    JOIN EMPLEADO E ON C.ID_USUARIO = E.ID_USUARIO
                    JOIN AUTH_USER US ON C.ID_USUARIO = US.ID          
                """)
                datos_empresa = cursor.fetchone()
                #/*SACA TOTALES DOCUMENTO*/
                cursor.execute(f"""
                    SELECT D.MONTO_NETO, D.IVA, D.MONTO_TOTAL
                    FROM DOCUMENTO D
                    WHERE D.ID_DOCUMENTO = {id} 
                """)
                doc_total = cursor.fetchone()
                nroOC = documento[12]
                #/*SACA SERVICIOS ADICIONALES */
                cursor.execute(f"""
                    SELECT COUNT(*)AS TT,DOC.ID_ORDEN_DE_COMPRA, SA.NOMBRE, ROUND(SUM(SA.PRECIO)/COUNT(*),2) AS UNITARIO, SUM(SA.PRECIO) AS TOTAL
                    FROM DETALLE_ORDEN_COMPRA DOC
                    LEFT JOIN DETALLE_SERVICIO_ADICIONAL DSA ON DOC.ID_DETALLE_ORDEN_DE_COMPRA = DSA.ID_DETALLE_ORDEN_DE_COMPRA
                    LEFT JOIN SERVICIO_ADICIONAL SA ON DSA.ID_SERVICIO = SA.ID_SERVICIO
                    WHERE DOC.ID_ORDEN_DE_COMPRA = {nroOC} /*VARIABLE 12*/
                    GROUP BY DOC.ID_ORDEN_DE_COMPRA, SA.NOMBRE, SA.PRECIO
                """)
                serv_ad = cursor.fetchall()
                if serv_ad[0][2] is None:
                    serv_ad = ''
                #/*SACA CANTIDAD Y RESUMEN DE COMEDORES */
                cursor.execute(f"""                
                    SELECT  COUNT(*) AS "0 CANT", ('Servicio de Comedor Tipo:'||' '|| (TC.DESCRIPCION)) AS "1 DES", ROUND(SUM(TC.PRECIO)/COUNT(*),2)AS "2 UNITARIO", SUM(TC.PRECIO) AS "3 TOTAL"
                    FROM DETALLE_ORDEN_COMPRA DOC
                    JOIN RESERVA R ON DOC.ID_DETALLE_ORDEN_DE_COMPRA = R.ID_DETALLE_ORDEN_DE_COMPRA
                    JOIN TIPO_COMEDOR TC ON R.ID_TIPO_COMEDOR = TC.ID_TIPO_COMEDOR
                    WHERE DOC.ID_ORDEN_DE_COMPRA = {nroOC} 
                    GROUP BY TC.DESCRIPCION, TC.PRECIO
                """)
                detcomedor = cursor.fetchall()
                #/*SACA CANTIDAD Y RESUMEN DE HABITACIONES */
                cursor.execute(f"""
                    SELECT  COUNT(*) AS "0 TT", ('Habitación' ||' '||TH.DESCRIPCION ||' Pieza N° '||H.NUMERO_HABITACION ) AS "1 DESCRIPCION", 
                    ROUND(SUM(H.PRECIO)/COUNT(*),2) AS "2 UNITARIO", SUM(H.PRECIO) AS "3 TOTAL"
                    FROM DETALLE_ORDEN_COMPRA DOC
                    JOIN RESERVA R ON DOC.ID_DETALLE_ORDEN_DE_COMPRA = R.ID_DETALLE_ORDEN_DE_COMPRA
                    JOIN HABITACION H ON R.ID_HABITACION  = H.ID_HABITACION
                    JOIN TIPO_HABITACION TH ON H.ID_TIPO_HABITACION = TH.ID_TIPO_HABITACION
                    WHERE DOC.ID_ORDEN_DE_COMPRA = {nroOC} 
                    GROUP BY ('Habitación' ||' '||TH.DESCRIPCION ||' Pieza N° '||H.NUMERO_HABITACION ), H.PRECIO
                """)
                habitaciones = cursor.fetchall()
        except Exception as e:
            print(e)
            pass
    data = {
        'documento':documento,
        'doc_total':doc_total,
        'serv_ad': serv_ad,
        'detcomedor':detcomedor,
        'habitaciones':habitaciones,
        'datos_empresa':datos_empresa
    }
    return render(request, 'Clientes/factura.html',data)

def nueva_opinion(request, id):
    opinion = None

    with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT OPINION FROM OPINION WHERE ID_ORDEN_DE_COMPRA = %s", [id])
                opinion = cursor.fetchone()[0]
            except Exception as e:
                print(e)

    if request.method == 'POST':
        opinion = request.POST['opinion']
        print(opinion)

        with connection.cursor() as cursor:
            try:
                #Insertar opinion
                cursor.execute("INSERT INTO OPINION (ID_ORDEN_DE_COMPRA, OPINION) VALUES(%s, %s)", [id, opinion])

                messages.success(request, 'Opinion enviada, agradecemos por tu tiempo')
                return redirect('oc-list')
            except Exception as e:
                print(e)

    data = {
        'orden_compra': id,
        'opinion': opinion
    }

    return render(request, 'Clientes/nueva-opinion.html', data)


# --------------------------FIN CLIENTES
