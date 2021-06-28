from django.shortcuts import render, redirect
from django.urls.conf import path
from Aplicaciones.app.models import User, Cliente, Huesped, TipoHabitacion, EstadoHabitacion, Habitacion, Accesorio
from django.contrib import messages
from django.db import connection
from datetime import datetime
from django.contrib.auth.hashers import PBKDF2PasswordHasher
import os
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from Aplicaciones.appADM.resources import HuespedResource
from tablib import Dataset
import cx_Oracle
# Create your views here.


# ***Módulo:Empleados*** Opción: inicio


def dashboard(request):
    clientes = ''
    hab_disponible = ''
    hab_total = ''
    empleados_new = ''
    clientes_new = ''
    reservas = ''
    ingresos = 0
    facturas = 0
    notacreditos = 0
    with connection.cursor() as cursor:
        try:
            cursor.execute("""SELECT COUNT(*) TT FROM AUTH_USER""")
            usuarios = cursor.fetchall()
            cursor.execute(f"""
            SELECT  SUM(MONTO_TOTAL) TTFE
                FROM DOCUMENTO WHERE CODIGO_SII = 33
            """)
            facturas = cursor.fetchone()[0]
            
            cursor.execute(f"""
            SELECT SUM(MONTO_TOTAL) TTFE
                FROM DOCUMENTO WHERE CODIGO_SII = 61
                                   
            """)                        
            notacreditos = cursor.fetchone()[0]
            
            ingresos = facturas-notacreditos
            cursor.execute(
                """SELECT COUNT(*) TT FROM CLIENTE WHERE ID_TIPO_CLIENTE = 1""")
            clientes = cursor.fetchall()
            cursor.execute(
                """SELECT COUNT(*) TT FROM HABITACION WHERE ID_ESTADO_HABITACION = 1 AND ESTADO = 1""")
            hab_disponible = cursor.fetchall()
            cursor.execute(
                """SELECT COUNT(*) TT FROM HABITACION WHERE ESTADO = 1""")
            hab_total = cursor.fetchall()
            cursor.execute("""      
                    SELECT CL.ID_CLIENTE, CL.RAZON_SOCIAL, US.DATE_JOINED 
                    FROM CLIENTE CL 
                    JOIN AUTH_USER US ON CL.ID_USUARIO = US.ID
                    WHERE ID_TIPO_CLIENTE = 1 AND rownum <= 5 ORDER BY US.DATE_JOINED DESC 
                    """)
            clientes_new = cursor.fetchall()
            cursor.execute("""
                    SELECT E.ID_EMPLEADO, (E.NOMBRES ||' '|| E.APELLIDO_P) AS NOMBRE, US.LAST_LOGIN 
                    FROM EMPLEADO E 
                    JOIN AUTH_USER US ON E.ID_USUARIO = US.ID 
                    WHERE ID_USUARIO != 1 and LAST_LOGIN != '' AND rownum<= 5 ORDER BY US.LAST_LOGIN DESC
                    """)
            empleados_new = cursor.fetchall()
            cursor.execute("""
            SELECT R.ID_RESERVA AS "0", DOC.id_orden_de_compra AS "1", CL.razon_social AS "2", (H.rut) AS "3 RUT",
                            (H.nombre ||' '|| H.apellido_p) AS "4 NOMBRE",TC.descripcion AS "5",HA.numero_habitacion AS "6",
                            THA.descripcion AS "7",  DOC.inicio_estadia AS "8 INI. ESTADIA", DOC.final_estadia AS "9 FIN. ESTADIA", 
                            R.check_in AS "10", H.DV AS "11"
                            FROM RESERVA R
                            JOIN DETALLE_ORDEN_COMPRA DOC ON R.ID_DETALLE_ORDEN_DE_COMPRA = DOC.ID_DETALLE_ORDEN_DE_COMPRA
                            JOIN ORDEN_COMPRA OC ON DOC.ID_ORDEN_DE_COMPRA = OC.ID_ORDEN_DE_COMPRA
                            JOIN HUESPED H ON R.ID_HUESPED = H.ID_HUESPED
                            JOIN CLIENTE CL ON OC.ID_CLIENTE = CL.ID_CLIENTE
                            JOIN TIPO_COMEDOR TC ON R.ID_TIPO_COMEDOR = TC.ID_TIPO_COMEDOR
                            JOIN HABITACION HA ON R.ID_HABITACION = HA.ID_HABITACION
                            JOIN TIPO_HABITACION THA ON HA.ID_TIPO_HABITACION = THA.ID_TIPO_HABITACION
                            LEFT JOIN PLATO_SEMANAL P ON R.PLATO = P.ID_COMEDOR
                            WHERE R.check_in = 0 order by DOC.inicio_estadia
            """)
            reservas = cursor.fetchall()
        except Exception as e:
            print(e)
            pass
    data = {
        'usuarios': usuarios,
        'ingresos':ingresos,
        'clientes': clientes,
        'hab_disponible': hab_disponible,
        'hab_total': hab_total,
        'empleados_new': empleados_new,
        'clientes_new': clientes_new,
        'reservas':reservas
    }
    return render(request, 'Empleados/dashboard.html', data)

# ***Módulo:Empleados*** Opción: clientes


def clientes(request):
    clientes = ''
    idTipoCliente = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT ID_TIPO_CLIENTE FROM TIPO_CLIENTE WHERE DESCRIPCION LIKE 'Cliente'")
            idTipoCliente = cursor.fetchone()
            idTipoCliente = idTipoCliente[0]
            cursor.execute(f"""SELECT CL.ID_CLIENTE, CL.RUT_EMPRESA, CL.DV, CL.RAZON_SOCIAL, US.DATE_JOINED,
            CL.ESTATUS FROM CLIENTE CL, AUTH_USER US WHERE CL.ID_USUARIO = US.ID AND CL.ID_TIPO_CLIENTE = {idTipoCliente}""")
            clientes = cursor.fetchall()
        except Exception as e:
            print(e)
            pass

    data = {
        'clientes': clientes
    }

    return render(request, 'Empleados/Clientes/clientes.html', data)


def eliminar_cliente(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute( f"UPDATE CLIENTE SET ESTATUS = 0 WHERE ID_CLIENTE = {id}")
        except Exception as e:
            print(e)
            pass

    messages.success(request, "Eliminado correctamente")
    return redirect(to="clientes-list")


def edit_clientes(request, id):
    usuario = ''
    comuna = ''
    region = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT ID_USUARIO, RUT_EMPRESA, DV, NOMBRE_COMERCIAL, RAZON_SOCIAL, ESTATUS, CELULAR, "
                           "COMUNA_ID, DIRECCION FROM CLIENTE WHERE ID_CLIENTE = %s", [id])
            cliente = cursor.fetchone()
            cliente_m = Cliente()
            cliente_m.rut_empresa = cliente[1]
            cliente_m.dv = cliente[2]
            cliente_m.nombre_comercial = cliente[3]
            cliente_m.razon_social = cliente[4]
            cliente_m.estatus = cliente[5]
            cliente_m.celular = cliente[6]
            cliente_m.direccion = cliente[8]
            if cliente_m.direccion == None:
                cliente_m.direccion = ''
            usuario = User.objects.get(id=cliente[0])
            if usuario is not None:
                cursor.execute("SELECT * FROM COMUNA")
                comunas = cursor.fetchall()

                cursor.execute("SELECT * FROM REGION")
                regiones = cursor.fetchall()

                if cliente[7] is not None:
                    cursor.execute(
                        "SELECT * FROM COMUNA WHERE COMUNA_ID = %s", [cliente[7]])
                    comuna = cursor.fetchone()

                    cursor.execute(
                        "SELECT * FROM REGION WHERE ID_REGION = %s", [comuna[2]])
                    region = cursor.fetchone()
        except Exception as e:
            print(e)
            messages.error(
                request, 'El Cliente que desea editar No Existe o fue eliminado')
            return redirect('clientes-list')

    if request.method == "POST":
        rut_empresa = request.POST['rut']
        nombre_comercial = request.POST['nom_fantasia']
        razon_social = request.POST['r_social']
        estatus = request.POST.get('emp-sel', None)
        email = request.POST['email']
        celular = request.POST['fono']
        comuna = request.POST.get('com_sel', None)
        direccion = request.POST['direccion']

        rut_empresa = rut_empresa.strip().lower()
        nombre_comercial = nombre_comercial.strip().lower()
        razon_social = razon_social.strip().lower()
        email = email.strip().lower()
        celular = celular.strip().lower()
        direccion = direccion.strip().lower()
        print(id)
        with connection.cursor() as cursor:
            try:
                pass
                cursor.execute(
                    "SELECT ID_USUARIO FROM CLIENTE WHERE ID_CLIENTE = %s", [id])
                cliente = cursor.fetchone()

                usuario = User.objects.get(id=cliente[0])
                usuario.email = email
                usuario.save()

                rut = rut_empresa

                # Limpia Rut de Puntos y Guión
                rut = rut.replace('.', "")
                rut = rut.replace('-', "")
                # Quita Digito Verificador
                rut = rut.rstrip(rut[-1])
                # Obtiene Digito Verificador
                dv = rut_empresa[-1]
                
                cursor.execute("UPDATE CLIENTE SET RUT_EMPRESA = %s, DV = %s, NOMBRE_COMERCIAL = %s, RAZON_SOCIAL = %s, "
                               "ESTATUS = %s, CELULAR = %s, COMUNA_ID = %s, DIRECCION = %s WHERE ID_CLIENTE = %s",
                               [rut, dv, nombre_comercial, razon_social, estatus, celular, comuna, direccion, id])

                messages.success(
                    request, f'El Cliente ' + razon_social.upper() + ' fue Modificado Correctamente')
                return redirect('clientes-list')
            except Exception as e:
                print(e)
                pass
    data = {
        'cliente': cliente_m,
        'usuario': usuario,
        'comunas': comunas,
        'comuna': comuna,
        'regiones': regiones,
        'region': region,

    }
    return render(request, 'Empleados/Clientes/edit_cliente.html', data)


def cliente_pass(request, id):
    cliente = ''  # Usuario vacio en caso de que no se cargue usuario
    idTipoCliente = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT ID_TIPO_CLIENTE FROM TIPO_CLIENTE WHERE DESCRIPCION LIKE 'Cliente'")
            idTipoCliente = cursor.fetchone()
            idTipoCliente = idTipoCliente[0]            
            cursor.execute(f"""
                SELECT ID_CLIENTE, (RUT_EMPRESA || '-' || DV )AS RUT,  RAZON_SOCIAL, ID_USUARIO
                FROM CLIENTE 
                WHERE ID_CLIENTE = {id} AND ID_TIPO_CLIENTE = {idTipoCliente}
            """)
            cliente = cursor.fetchone()
            idActualiza = cliente[3]
            rut = cliente[1]
        except Exception as e:
            messages.error(
                request, 'El Cliente que buscó No Existe o fue eliminado')
            return redirect('clientes-list')
    if request.method == "POST":
        pwd1 = request.POST['new_pwd']
        pwd2 = request.POST['conf_new_pwd']
        pwd1 = pwd1.strip().lower()
        pwd2 = pwd2.strip().lower()
        if len(pwd1) >= 8 and len(pwd2) >= 8:
            if pwd1 != pwd2:
                messages.error(
                    request, 'La Contraseñas Ingresadas No son Identicas, Corrija e Intente de Nuevo')
            else:
                hasher = PBKDF2PasswordHasher()
                pwdEncriptado = hasher.encode(password=pwd1,
                                              salt='salt',
                                              iterations=260000)

                with connection.cursor() as cursor:
                    try:
                        cursor.execute(f"""
                            UPDATE AUTH_USER SET PASSWORD = '{pwdEncriptado}'
                            WHERE ID = {idActualiza}
                        """)
                        messages.success(
                            request, f'Se ha Restablecido la Contraseña del Usuario: ' + rut + ' Correctamente')
                        return redirect('clientes-list')

                    except Exception as e:
                        print(e)
                        pass
        else:
            messages.error(
                request, 'El Largo de La Contraseña es mínimo de 8 caracteres')
    data = {
        'cliente': cliente
    }
    return render(request, 'Empleados/Clientes/pass_cliente.html', data)
# ***Módulo:Empleados*** Opción: empleados


def nuevo_empleado(request):
    fec_nac = ''
    validaUs = 0
    nombre = ''
    apellido_p = ''
    apellido_m = ''
    email = ''
    fono = ''
    nacionalidad = ''
    rut = ''
    direccion = ''
    fec_nac = ''
    tipo_empleados = ''
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM COMUNA")
        comunas = cursor.fetchall()
        cursor.execute("SELECT * FROM REGION")
        regiones = cursor.fetchall()
        cursor.execute("SELECT * FROM TIPO_EMPLEADO WHERE ESTATUS = 1")
        tipo_empleados = cursor.fetchall()
        print(tipo_empleados)

    if request.method == 'POST':
        pwd1 = request.POST['password1']
        pwd2 = request.POST['password2']
        if (pwd1 != pwd2):
            messages.error(
                request, 'La Contraseñas Ingresadas No son Identicas, Corrija e Intente de Nuevo')
        else:
            nombre = request.POST['nombre']
            apellido_p = request.POST['apellido_p']
            apellido_m = request.POST['apellido_m']
            email = request.POST['email']
            fono = request.POST['fono']
            fec_nac = request.POST['fec_nac']
            nacionalidad = request.POST['nacionalidad']
            estado = request.POST['estado']
            ge_pedido = request.POST['ge_pedido']
            tipo_e = request.POST['tipo_e']
            rut = request.POST['rut']
            com_sel = request.POST['com_sel']
            direccion = request.POST['direccion']
            nombre = nombre.strip()
            apellido_p = apellido_p.strip()
            apellido_m = apellido_m.strip()
            email = email.strip()
            fono = fono.strip()
            nacionalidad = nacionalidad.strip()
            rut = rut.strip()
            direccion = direccion.strip()
            id_empleadoUs = ''
            # Limpia Rut de Puntos y Guión
            rut2 = rut.replace('.', "")
            rut2 = rut2.replace('-', "")
            # Quita Digito Verificador
            vrutSinDv = rut2.strip(rut2[-1])

            # Obtiene Digito Verificador
            dv = rut2[-1]
            if len(nombre) > 0 and len(apellido_p) > 0 and len(apellido_m) >= 0 and len(email) > 0 and len(fono) >= 0   \
                    and len(tipo_e) > 0 and len(rut) > 0 and len(com_sel) >= 0 and len(direccion) >= 0:
                print(vrutSinDv)
                with connection.cursor() as cursor:
                    cursor.execute(f"""
                    SELECT COUNT(*) AS TT  FROM EMPLEADO E JOIN AUTH_USER AU ON  TO_CHAR (E.RUT_EMPLEADO) = AU.USERNAME
                    WHERE E.RUT_EMPLEADO = '{vrutSinDv}' or AU.USERNAME = '{vrutSinDv}'
                    """)
                    validaUs = cursor.fetchone()
                    print(validaUs[0])
                    if validaUs[0] >= 1:
                        messages.error(
                            request, 'Rut Ingresado ya pertenece a un Empleado, modifique e intente de nuevo')
                    else:
                        cursor.execute(
                            f"SELECT COUNT(*) AS TT  FROM AUTH_USER WHERE EMAIL = '{email}'")
                        validaEmail = cursor.fetchall()
                        if validaEmail[0][0] >= 1:
                            messages.error(
                                request, 'Email Ingresado ya está registrado en el sistema, modifique e intente de nuevo')
                        else:
                            print('seguimos al insert')
                            # Se crea encriptado de Contraseña
                            hasher = PBKDF2PasswordHasher()
                            pwdEncriptado = hasher.encode(password=pwd1,
                                                          salt='salt',
                                                          iterations=260000)
                            # Variable fecha actual
                            now = datetime.now()
                            formato = '%d/%m/%Y'
                            #Se valida fecha de nacimiento
                            if len(fec_nac)>0:
                                #Se transforma fecha STR a DATE
                                fecha_nac_obj = datetime.strptime(fec_nac,'%Y-%m-%d' )          
                            print(fecha_nac_obj)
                            with connection.cursor() as cursor:
                                try:
                                    # Inserción de Datos en Tabla Usuarios
                                    print('entro a insert US')
                                    cursor.execute(f"""                                
                                           INSERT INTO AUTH_USER (PASSWORD, IS_SUPERUSER,USERNAME, FIRST_NAME, LAST_NAME, EMAIL, IS_STAFF, IS_ACTIVE, DATE_JOINED, IS_CLIENTE, IS_EMPLEADO, IS_PROVEEDOR)
                                                   VALUES('{pwdEncriptado}', '0',{vrutSinDv}, '{nombre}', '{apellido_p}', '{email}', '0', '{estado}', '{now}', 0 , 1 , 0  )
                                    """)
                                    print('salgo a insert US')
                                    cursor.execute(
                                        f"""SELECT ID FROM AUTH_USER WHERE USERNAME = '{vrutSinDv}'""")
                                    id_emp = cursor.fetchone()
                                   
                                    # Inserción de Datos en Tabla Empleados
                                    id_empleadoUs = id_emp[0]
                                    print('ID EMPLEADO',id_empleadoUs)
                                    if id_empleadoUs > 0:
                                        print(id_empleadoUs)
                                        cursor.execute(f"""                                
                                            INSERT INTO EMPLEADO (ESTATUS, NOMBRES, APELLIDO_P, APELLIDO_M, RUT_EMPLEADO, DV, CELULAR, NACIMIENTO, NACIONALIDAD, DIRECCION, PEDIDOS, COMUNA_ID, ID_TIPO, ID_USUARIO  )
                                                    VALUES('{estado}', '{nombre}', '{apellido_p}', '{apellido_m}',{vrutSinDv}, '{dv}','{fono}', '{fecha_nac_obj}', '{nacionalidad}', '{direccion}', {ge_pedido}, {com_sel}, {tipo_e}, {id_empleadoUs} )
                                        """)
                                        messages.success(
                                            request, f'El Empleado de Rut {rut} se ha creado de manera correcta')
                                        return redirect('empleado-new')
                                    else:
                                        messages.error(
                                            request, f'Error en ID de Usuario Empleado')
                                except Exception as e:
                                    print(e)
                           

    data = {
        'comunas': comunas,
        'regiones': regiones,
        'tipo_empleados': tipo_empleados,
        'nombre': nombre,
        'apellido_p': apellido_p,
        'apellido_m': apellido_m,
        'email': email,
        'fono': fono,
        'fec_nac': fec_nac,
        'nacionalidad': nacionalidad,
        'rut': rut,
        'direccion': direccion
    }
    return render(request, 'Empleados/Empleados/empleado.html', data)


def edit_empleado(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"""
                SELECT E.ID_USUARIO AS "0", AU.USERNAME AS "1", E.NOMBRES AS "2", E.APELLIDO_P AS "3", E.APELLIDO_M AS "4", AU.EMAIL AS "5",
                        E.CELULAR AS "6",
                        TO_CHAR(NACIMIENTO,'YYYY-MM-DD') AS "7", NACIONALIDAD AS "8",
                        E.ESTATUS AS "9", E.ID_TIPO AS "10", (E.RUT_EMPLEADO ||'-'|| E.DV) AS "11" ,
                        E.PEDIDOS AS "12", E.COMUNA_ID AS "13", E.DIRECCION AS "14"
                        FROM EMPLEADO E
                        JOIN AUTH_USER AU ON E.ID_USUARIO = AU.ID
                        WHERE ID_EMPLEADO = {id} and ID_USUARIO !=1
                """)
            trabajador = cursor.fetchone()
            fechaT = trabajador[7]
            ape_materno =  trabajador[4]
            us_nacionalidad = trabajador[8]
            if fechaT:
                fecha = fechaT
            else:
                fecha = ''            
            if ape_materno:
                ape_materno = ape_materno
            else:
                ape_materno = ''
            if us_nacionalidad:
                us_nacionalidad = us_nacionalidad
            else:
                us_nacionalidad = ''                
            cursor.execute("SELECT * FROM TIPO_EMPLEADO")
            tipo_empleados = cursor.fetchall()

            cursor.execute("SELECT * FROM COMUNA")
            comunas = cursor.fetchall()

            cursor.execute("SELECT * FROM REGION")
            regiones = cursor.fetchall()

            if trabajador[10] is not None:
                cursor.execute(
                    "SELECT * FROM TIPO_EMPLEADO WHERE ID_TIPO = %s", [trabajador[10]])
                tipo_empleado = cursor.fetchone()
            if trabajador[13] is not None:
                cursor.execute(
                    "SELECT * FROM COMUNA WHERE COMUNA_ID = %s", [trabajador[13]])
                comuna = cursor.fetchone()

                cursor.execute(
                    "SELECT * FROM REGION WHERE ID_REGION = %s", [comuna[2]])
                region = cursor.fetchone()

        except Exception as e:
            print(e)
            print(f"""
                SELECT E.ID_USUARIO AS "0", AU.USERNAME AS "1", E.NOMBRES AS "2", E.APELLIDO_P AS "3", E.APELLIDO_M AS "4", AU.EMAIL AS "5",
                        E.CELULAR AS "6",
                        TO_CHAR(NACIMIENTO,'YYYY-MM-DD') AS "7", NACIONALIDAD AS "8",
                        E.ESTATUS AS "9", E.ID_TIPO AS "10", (E.RUT_EMPLEADO ||'-'|| E.DV) AS "11" ,
                        E.PEDIDOS AS "12", E.COMUNA_ID AS "13", E.DIRECCION AS "14"
                        FROM EMPLEADO E
                        JOIN AUTH_USER AU ON E.ID_USUARIO = AU.ID
                        WHERE ID_USUARIO = {id} and ID_USUARIO !=1
                """)
            messages.error(
                request, 'El Empleado que desea editar No Existe o fue eliminado')
            return redirect('empleados-list')
    if request.method == "POST":
        nombre = request.POST['nombre']
        apellido_p = request.POST['apellido_p']
        apellido_m = request.POST['apellido_m']
        email = request.POST['email']
        fono = request.POST['fono']
        fec_nac = request.POST['fec_nac']
        nacionalidad = request.POST['nacionalidad']
        estado = request.POST['estado']
        tipo_e = request.POST['tipo_e']
        rut = request.POST['rut']
        ge_pedido = request.POST['ge_pedido']
        com_sel = request.POST['com_sel']
        direccion = request.POST['direccion']

        nombre = nombre.strip().lower()
        apellido_p = apellido_p.strip().lower()
        apellido_m = apellido_m.strip().lower()
        email = email.strip().lower()
        fono = fono.strip()
        fec_nac = fec_nac.strip()
        nacionalidad = nacionalidad.strip().lower()
        estado = estado.strip()
        tipo_e = tipo_e.strip()
        ge_pedido = ge_pedido.strip()
        com_sel = com_sel.strip()
        direccion = direccion.strip().lower()
        rut = rut.strip()
        # Limpia Rut de Puntos y Guión
        rut2 = rut.replace('.', "")
        rut2 = rut2.replace('-', "")
        # Quita Digito Verificador
        vrutSinDv = rut2.strip(rut2[-1])

        # Obtiene Digito Verificador
        dv = rut2[-1]
        if len(nombre) > 0 and len(apellido_p) > 0 and len(apellido_m) >= 0 and len(email) > 0 and len(fono) >= 0   \
                and len(tipo_e) > 0 and len(rut) > 0 and len(com_sel) >= 0 and len(direccion) >= 0:

            with connection.cursor() as cursor:
                try:
                    pass
                    cursor.execute(f"SELECT COUNT(*)TT FROM EMPLEADO WHERE RUT_EMPLEADO = {vrutSinDv} AND DV = {dv} and ID_EMPLEADO != {id}")
                    validaRut = cursor.fetchone()[0]
                    if int(validaRut)>0:
                        messages.error(request, 'El Rut Ingresado Ya Pertenece a un Empleado')
                    else:
                        cursor.execute(
                            "SELECT ID_USUARIO FROM EMPLEADO WHERE ID_EMPLEADO = %s", [id])
                        cliente = cursor.fetchone()

                        usuario = User.objects.get(id=trabajador[0])
                        usuario.email = email
                        usuario.username = vrutSinDv
                        usuario.first_name = nombre
                        usuario.last_name = apellido_p
                        usuario.is_active = estado
                        usuario.save()
                        print('update')
                        if len(fec_nac)>0:
                            #Se transforma fecha STR a DATE
                            fecha_nac_obj = datetime.strptime(fec_nac,'%Y-%m-%d' )          
                            print(fecha_nac_obj)
                        cursor.execute(f"""UPDATE EMPLEADO SET ESTATUS = '{estado}', NOMBRES = '{nombre}', APELLIDO_P = '{apellido_p}',
                                            APELLIDO_M = '{apellido_m}',  RUT_EMPLEADO = '{vrutSinDv}', DV = '{dv}', CELULAR = '{fono}',
                                            NACIMIENTO = '{fecha_nac_obj}', PEDIDOS = '{ge_pedido}', COMUNA_ID = '{com_sel}', ID_TIPO = '{tipo_e}'
                                            WHERE ID_EMPLEADO = {id}
                                            """)
                        messages.success(
                            request, f'El Empleado de Rut ' + rut + ' fue Modificado Correctamente')
                        return redirect('empleados-list')
                except Exception as e:
                    print(e)
                    pass
    data = {
        'trabajador': trabajador,
        'fecha': fecha,
        'comunas': comunas,
        'regiones': regiones,
        'comuna': comuna,
        'region': region,
        'tipo_empleados': tipo_empleados,
        'tipo_empleado': tipo_empleado,
        'ape_materno':ape_materno,
        'us_nacionalidad':us_nacionalidad
    }
    return render(request, 'Empleados/Empleados/edit_empleado.html', data)


def empleados(request):
    trabajadores = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                SELECT E.ID_EMPLEADO, (E.RUT_EMPLEADO || '-' || E.DV )AS RUT,  (E.NOMBRES ||' ' || E.APELLIDO_P) AS NOMBRE ,
                    TE.DESCRIPCION,AU.DATE_JOINED, E.ESTATUS, E.PEDIDOS
                FROM EMPLEADO E
                JOIN TIPO_EMPLEADO TE ON E.ID_TIPO = TE.ID_TIPO
                JOIN AUTH_USER AU ON TO_CHAR(E.RUT_EMPLEADO) = AU.USERNAME 
            """)
            trabajadores = cursor.fetchall()

        except Exception as e:
            print(e)
            pass

    data = {
        'trabajadores': trabajadores
    }
    return render(request, 'Empleados/Empleados/empleados.html', data)


def eliminar_empleado(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"SELECT ID_USUARIO FROM EMPLEADO WHERE ID_EMPLEADO = {id}")
            idUsuario = cursor.fetchone()[0]
            cursor.execute(
                "UPDATE EMPLEADO SET ESTATUS = %s WHERE ID_USUARIO = %s", [0, idUsuario])
            cursor.execute(
                "UPDATE AUTH_USER SET IS_ACTIVE = %s WHERE ID_USUARIO = %s", [0, idUsuario])
        except Exception as e:
            print(e)
            pass

    messages.success(request, "El Empleado fue Eliminado correctamente")
    return redirect(to="empleados-list")


def empleado_pass(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"""
                SELECT ID_USUARIO, (RUT_EMPLEADO || '-' || DV )AS RUT,  (NOMBRES ||' ' || APELLIDO_P) AS NOMBRE
                FROM EMPLEADO 
                WHERE ID_EMPLEADO = {id}
            """)
            empleado = cursor.fetchone()
            rut = empleado[1]
        except Exception as e:
            messages.error(
                request, 'El Empleado que buscó No Existe o fue eliminado')
            return redirect('empleados-list')

    if request.method == "POST":
        pwd1 = request.POST['new_pwd']
        pwd2 = request.POST['conf_new_pwd']
        pwd1 = pwd1.strip().lower()
        pwd2 = pwd2.strip().lower()
        if len(pwd1) >= 8 and len(pwd2) >= 8:
            if pwd1 != pwd2:
                messages.error(
                    request, 'La Contraseñas Ingresadas No son Identicas, Corrija e Intente de Nuevo')
            else:
                hasher = PBKDF2PasswordHasher()
                pwdEncriptado = hasher.encode(password=pwd1,
                                              salt='salt',
                                              iterations=260000)

                with connection.cursor() as cursor:
                    try:
                        cursor.execute(f"""
                            UPDATE AUTH_USER SET PASSWORD = '{pwdEncriptado}'
                            WHERE ID = {id}
                        """)
                        messages.success(
                            request, f'Se ha Restablecido la Contraseña del Usuario: ' + rut + ' Correctamente')
                        return redirect('empleados-list')

                    except Exception as e:
                        print(e)
                        pass
        else:
            messages.error(
                request, 'El Largo de La Contraseña es mínimo de 8 caracteres')

    data = {
        'empleado': empleado
    }
    return render(request, 'Empleados/Empleados/pass_empleado.html', data)


def tipo_empleado(request):
    tipo_empleados = ''
    nombre_tipo = ''
    estado = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                SELECT *
                FROM TIPO_EMPLEADO 
            """)
            tipo_empleados = cursor.fetchall()

        except Exception as e:
            print(e)
            pass
    if request.method == "POST":
        nombre_tipo = request.POST['cargo']
        estado = request.POST['estado']
        nombre_tipo = nombre_tipo.strip()
        if len(nombre_tipo) > 0 and len(estado) > 0:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        f"""SELECT COUNT(*)TT FROM TIPO_EMPLEADO WHERE DESCRIPCION LIKE '{nombre_tipo}' """)
                    validaExistencia = cursor.fetchone()
                    if validaExistencia[0] > 0:
                        messages.error(
                            request, f'El Cargo con nombre {nombre_tipo} Ya existe')
                    else:
                        cursor.execute(
                            f"""INSERT INTO TIPO_EMPLEADO (ESTATUS, DESCRIPCION) VALUES ({estado}, '{nombre_tipo}')""")
                        messages.success(
                            request, f'Se ha registrado un Nuevo Cargo con nombre {nombre_tipo}')
                        return redirect('tipo-empleado')
                except Exception as e:
                    print(e)
                    pass
        else:
            messages.error(
                request, f'Campo Cargo y Estado Obligatorios. Completelos para Continuar')
    data = {
        'tipo_empleados': tipo_empleados
    }

    return render(request, 'Empleados/Empleados/tipo_empleado.html', data)


def editar_tipoEmpleado(request, id):
    tipo_e = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"SELECT * FROM TIPO_EMPLEADO WHERE ID_TIPO = {id}")
            tipo_e = cursor.fetchone()
            if not tipo_e:
                messages.error(
                    request, 'El Tipo de Empleado que desea editar No Existe o fue eliminado')
                return redirect('tipo-empleado')
        except Exception as e:
            print(e)
            pass
    if request.method == "POST":
        nombre_tipo = request.POST['cargo']
        estado = request.POST['estado']
        nombre_tipo = nombre_tipo.strip()

        if len(nombre_tipo) > 0 and len(estado) > 0:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        f"""SELECT COUNT(*)TT FROM TIPO_EMPLEADO WHERE DESCRIPCION LIKE '{nombre_tipo}' AND ID_TIPO != {id}""")
                    validaExistencia = cursor.fetchone()
                    if validaExistencia[0] > 0:
                        messages.error(
                            request, f'El Cargo con nombre {nombre_tipo} Ya existe')
                    else:
                        cursor.execute(
                            f"""UPDATE TIPO_EMPLEADO SET ESTATUS = {estado}, DESCRIPCION='{nombre_tipo}' WHERE ID_TIPO = {id} """)
                        messages.success(
                            request, f'Se ha Modificado el Tipo de Empleado con nombre {nombre_tipo} Correctamente')
                        return redirect('tipo-empleado')
                except Exception as e:
                    print(e)
                    pass
        else:
            messages.error(
                request, f'Campo Cargo y Estado Obligatorios. Completelos para Continuar')
    data = {
        'tipo_e': tipo_e,
    }
    return render(request, 'Empleados/Empleados/edit_tipo_emp.html', data)


def eliminar_tipoEmpleado(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "UPDATE TIPO_EMPLEADO SET ESTATUS = %s WHERE ID_TIPO = %s", [0, id])
            messages.success(
                request, 'Tipo de empleado eliminado Correctamente')
        except Exception as e:
            print(e)
            pass
    return redirect('tipo-empleado')

# ***Módulo:Empleados*** Opción: proveedores


def nuevo_proveedor(request):
    rut = ''
    r_social = ''
    nom_fantasia = ''
    username = ''
    email = ''
    fono = ''
    direccion = ''
    validaUs = 0
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM COMUNA")
        comunas = cursor.fetchall()
        cursor.execute("SELECT * FROM REGION")
        regiones = cursor.fetchall()

    if request.method == 'POST':
        pwd1 = request.POST['password1']
        pwd2 = request.POST['password2']
        if (pwd1 != pwd2):
            messages.error(
                request, 'La Contraseñas Ingresadas No son Identicas, Corrija e Intente de Nuevo')
        else:
            rut = request.POST['rut']
            r_social = request.POST['r_social']
            nom_fantasia = request.POST['nom_fantasia']
            username = request.POST['username']
            email = request.POST['email']
            fono = request.POST['fono']
            estado = request.POST['estado']
            com_sel = request.POST['com_sel']
            direccion = request.POST['direccion']
            r_social = r_social.strip()
            nom_fantasia = nom_fantasia.strip()
            username = username.strip().lower()
            email = email.strip().lower()
            fono = fono.strip()
            rut = rut.strip().lower()
            direccion = direccion.strip()
            # Limpia Rut de Puntos y Guión
            rut2 = rut.replace('.', "")
            rut2 = rut2.replace('-', "")
            # Quita Digito Verificador
            vrutSinDv = rut2.strip(rut2[-1])

            # Obtiene Digito Verificador
            dv = rut2[-1]
            if len(rut) > 0 and len(r_social) > 0 and len(nom_fantasia) >= 0 and len(username) > 0 and len(email) > 0 and len(fono) >= 0   \
                    and len(com_sel) >= 0 and len(direccion) >= 0:
                print(vrutSinDv)
                with connection.cursor() as cursor:
                    cursor.execute("SELECT ID_TIPO_CLIENTE FROM TIPO_CLIENTE WHERE DESCRIPCION LIKE 'Proveedor'")
                    idTipoCliente = cursor.fetchone()[0]                    
                    cursor.execute(f"""
                    SELECT COUNT(*) AS TT  FROM CLIENTE 
                    WHERE RUT_EMPRESA = '{vrutSinDv}' AND ID_TIPO_CLIENTE = {idTipoCliente} 
                    """)
                    validaRut = cursor.fetchall()
                    print(validaRut[0][0])
                    if validaRut[0][0] >= 1:
                        messages.error(
                            request, 'Rut Ingresado ya pertenece a un Proveedor, modifique e intente de nuevo')
                    else:
                        cursor.execute(f"""
                        SELECT COUNT(*) AS TT  FROM AUTH_USER 
                        WHERE USERNAME = '{username}' 
                        """)
                        validaUs = cursor.fetchall()
                        print(validaUs[0][0])
                        if validaUs[0][0] >= 1:
                            messages.error(
                                request, 'Nombre de Usuario Ingresado No se encuentra disponible, modifique e intente de nuevo')
                        else:
                            cursor.execute(
                                f"SELECT COUNT(*) AS TT  FROM AUTH_USER WHERE EMAIL = '{email}'")
                            validaEmail = cursor.fetchall()
                            if validaEmail[0][0] >= 1:
                                messages.error(
                                    request, 'Email Ingresado ya está registrado en el sistema, modifique e intente de nuevo')
                            else:
                                print('seguimos al insert')
                                # Se crea encriptado de Contraseña
                                hasher = PBKDF2PasswordHasher()
                                pwdEncriptado = hasher.encode(password=pwd1,
                                                              salt='salt',
                                                              iterations=260000)
                                # Variable fecha actual
                                now = datetime.now()
                                with connection.cursor() as cursor:
                                    try:
                                        # Inserción de Datos en Tabla Usuarios
                                        cursor.execute(f"""                                
                                            INSERT INTO AUTH_USER (PASSWORD, IS_SUPERUSER,USERNAME, FIRST_NAME, LAST_NAME,  EMAIL, IS_STAFF, IS_ACTIVE, DATE_JOINED, IS_CLIENTE, IS_EMPLEADO, IS_PROVEEDOR)
                                                    VALUES('{pwdEncriptado}', '0','{username}', '{r_social}', '', '{email}', '0', '{estado}', '{now}', 0 , 0 , 1  )
                                        """)
                                        cursor.execute(
                                            f"""SELECT ID FROM AUTH_USER WHERE USERNAME = '{username}'""")
                                        id_emp = cursor.fetchone()
                                        # Inserción de Datos en Tabla Empleados
                                        id_empleadoUs = id_emp[0]
                                        print('id empleado',id_emp)
                                        if id_empleadoUs > 0:
                                            print(id_empleadoUs)
                                                                                     
                                            codigo_db = 0
                                            codigo = 0
                                            try:
                                                cursor.execute("SELECT MAX(CODIGO) FROM CLIENTE")

                                                codigo_db = cursor.fetchone()
                                                codigo = codigo_db[0]

                                                if codigo < 999:
                                                    codigo = codigo + 1
                                            except Exception as e:
                                                print(e)
                                                codigo = 1
                                            
                                            print("Ingresando a Insert Cliente")
                                            cursor.execute(f"""                                
                                                INSERT INTO CLIENTE (ESTATUS, RAZON_SOCIAL,  RUT_EMPRESA, DV, DIRECCION, CELULAR, NOMBRE_COMERCIAL,  COMUNA_ID, ID_TIPO_CLIENTE, ID_USUARIO, CODIGO)
                                                                    VALUES({estado}, '{r_social}', '{vrutSinDv}', '{dv}','{direccion}','{fono}', '{nom_fantasia}','{com_sel}', '{idTipoCliente}',  {id_empleadoUs} , {codigo})
                                            """)
                                            messages.success(
                                                request, f'El Proveedor de Rut {rut} se ha creado de manera correcta')
                                            return redirect('proveedor-new')
                                    except Exception as e:
                                        print(e)
                                        pass
    data = {
        'comunas': comunas,
        'regiones': regiones,
        'rut': rut,
        'r_social': r_social,
        'nom_fantasia': nom_fantasia,
        'username': username,
        'email': email,
        'fono': fono,
        'direccion': direccion
    }

    return render(request, 'Empleados/Proveedores/proveedor.html', data)


def edit_proveedor(request, id):
    celular = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT ID_TIPO_CLIENTE FROM TIPO_CLIENTE WHERE DESCRIPCION LIKE 'Proveedor'")
            idTipoCliente = cursor.fetchone()[0]               
            cursor.execute(f"""
                    SELECT C.ID_USUARIO AS "0",(C.RUT_EMPRESA ||'-'|| C.DV) AS "1",C.RAZON_SOCIAL  AS "2", C.NOMBRE_COMERCIAL AS "3", AU.USERNAME AS "4",
                        AU.EMAIL AS "5", C.CELULAR AS "6", 
                        C.ESTATUS AS "7", C.COMUNA_ID AS "8", C.DIRECCION AS "9"
                        FROM CLIENTE C
                        JOIN AUTH_USER AU ON C.ID_USUARIO = AU.ID
                        WHERE C.ID_CLIENTE = {id}  AND C.ID_TIPO_CLIENTE = {idTipoCliente}
                """)
            proveedor = cursor.fetchone()
            if proveedor[6]:
                celular = proveedor[6]
            else:
                celular = ''
            cursor.execute("SELECT * FROM COMUNA")
            comunas = cursor.fetchall()

            cursor.execute("SELECT * FROM REGION")
            regiones = cursor.fetchall()
            print('imprimo region',proveedor[8])
            if proveedor[8] is not None:
                cursor.execute(
                    "SELECT * FROM COMUNA WHERE COMUNA_ID = %s", [proveedor[8]])
                comuna = cursor.fetchone()

                cursor.execute(
                    "SELECT * FROM REGION WHERE ID_REGION = %s", [comuna[2]])
                region = cursor.fetchone()
        except Exception as e:
            print(e)
            print('me cai')
            messages.error(
                request, 'El Proveedor que desea editar No Existe o fue eliminado')
            return redirect('proveedores-list')
    if request.method == "POST":
        rut = request.POST['rut']
        r_social = request.POST['r_social']
        nom_fantasia = request.POST['nom_fantasia']
        email = request.POST['email']
        fono = request.POST['fono']
        estado = request.POST['estado']
        com_sel = request.POST['com_sel']
        direccion = request.POST['direccion']
        r_social = r_social.strip()
        nom_fantasia = nom_fantasia.strip()
        email = email.strip().lower()
        fono = fono.strip()
        rut = rut.strip().lower()
        direccion = direccion.strip()
        # Limpia Rut de Puntos y Guión
        rut2 = rut.replace('.', "")
        rut2 = rut2.replace('-', "")
        # Quita Digito Verificador
        vrutSinDv = rut2.strip(rut2[-1])

        # Obtiene Digito Verificador
        dv = rut2[-1]
        if len(rut) > 0 and len(r_social) > 0 and len(nom_fantasia) >= 0 and len(email) > 0 and len(fono) >= 0   \
                and len(com_sel) >= 0 and len(direccion) >= 0:
            with connection.cursor() as cursor:
                try:
                    pass

                    usuario = User.objects.get(id=proveedor[0])
                    usuario.email = email
                    usuario.first_name = r_social
                    usuario.last_name = ''
                    usuario.is_active = estado
                    usuario.save()

                    cursor.execute(f"""UPDATE CLIENTE SET ESTATUS = {estado}, RAZON_SOCIAL = '{r_social}',
                                        RUT_EMPRESA = {vrutSinDv}, DV = '{dv}', DIRECCION = '{direccion}', CELULAR = '{fono}',
                                        COMUNA_ID = '{com_sel}', nombre_comercial = '{nom_fantasia}'
                                        WHERE ID_CLIENTE = {id}
                                    """)
                    messages.success(
                        request, f'El Proveedor de Rut ' + rut + ' fue Modificado Correctamente')
                    return redirect('proveedores-list')
                except Exception as e:
                    print(e)
                    pass
    data = {
        'proveedor': proveedor,
        'comunas': comunas,
        'regiones': regiones,
        'region':region,
        'comuna': comuna,
        'celular':celular
    }
    return render(request, 'Empleados/Proveedores/edit_proveedor.html', data)


def eliminar_proveedor(request, id):
    with connection.cursor() as cursor:
        try:

            cursor.execute(f"SELECT ID_USUARIO FROM CLIENTE WHERE ID_CLIENTE = {id}")
            idProveedor = cursor.fetchone()[0]
            cursor.execute(
                "UPDATE CLIENTE SET ESTATUS = %s WHERE ID_USUARIO = %s", [0, idProveedor])
            cursor.execute(
                "UPDATE AUTH_USER SET IS_ACTIVE = %s WHERE ID_USUARIO = %s", [0, idProveedor])
        except Exception as e:
            print(e)
            pass

    messages.success(request, "El Empleado fue Eliminado correctamente")
    return redirect(to="proveedores-list")


def proveedores(request):
    proveedores = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT ID_TIPO_CLIENTE FROM TIPO_CLIENTE WHERE DESCRIPCION LIKE 'Proveedor'")
            idTipo = cursor.fetchone()[0]
            cursor.execute(f"""
                SELECT C.ID_USUARIO AS "0", (C.RUT_EMPRESA || '-' || C.DV )AS "1",  C.RAZON_SOCIAL AS "2",
                    AU.DATE_JOINED AS "3", C.ESTATUS AS "4", C.ID_CLIENTE AS "5"
                FROM CLIENTE C            
                JOIN AUTH_USER AU ON C.ID_USUARIO = AU.ID  WHERE C.ID_TIPO_CLIENTE = {idTipo}
            """)
            proveedores = cursor.fetchall()
            print(proveedores)
        except Exception as e:
            print(e)
            pass

    data = {
        'proveedores': proveedores
    }
    return render(request, 'Empleados/Proveedores/proveedores.html', data)


def proveedor_pass(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"""
                SELECT ID_USUARIO, (RUT_EMPRESA || '-' || DV )AS RUT,  RAZON_SOCIAL, ID_USUARIO
                FROM CLIENTE 
                WHERE ID_CLIENTE = {id}
            """)
            proveedor = cursor.fetchone()
            idActualiza = proveedor[3]
            rut = proveedor[1]
        except Exception as e:
            messages.error(
                request, 'El Proveedor que desea editar No Existe o fue eliminado')
            return redirect('proveedores-list')
    if request.method == "POST":
        pwd1 = request.POST['new_pwd']
        pwd2 = request.POST['conf_new_pwd']
        pwd1 = pwd1.strip().lower()
        pwd2 = pwd2.strip().lower()
        if len(pwd1) >= 8 and len(pwd2) >= 8:
            if pwd1 != pwd2:
                messages.error(
                    request, 'La Contraseñas Ingresadas No son Identicas, Corrija e Intente de Nuevo')
            else:
                hasher = PBKDF2PasswordHasher()
                pwdEncriptado = hasher.encode(password=pwd1,
                                              salt='salt',
                                              iterations=260000)

                with connection.cursor() as cursor:
                    try:
                        cursor.execute(f"""
                            UPDATE AUTH_USER SET PASSWORD = '{pwdEncriptado}'
                            WHERE ID = {idActualiza}
                        """)
                        messages.success(
                            request, f'Se ha Restablecido la Contraseña del Usuario: ' + rut + ' Correctamente')
                        return redirect('proveedores-list')

                    except Exception as e:
                        print(e)
                        pass
        else:
            messages.error(
                request, 'El Largo de La Contraseña es mínimo de 8 caracteres')
    data = {
        'proveedor': proveedor
    }
    return render(request, 'Empleados/Proveedores/pass_proveedor.html', data)
# ***Módulo:Empleados*** Opción: huéspedes


def huespedes(request):
    huespedes_list = ''
    idUsuario = ''
    with connection.cursor() as cursor:
        try:
            if request.user.is_cliente:
                idUsuario  = request.user.id
                cursor.execute(f"SELECT ID_CLIENTE FROM CLIENTE WHERE ID_USUARIO = {idUsuario} ")
                idCliente = cursor.fetchone()[0]
                cursor.execute("""SELECT H.ID_HUESPED AS "0", (C.RUT_EMPRESA ||'-'|| C.DV)  AS "1_RUT_E", (H.RUT ||'-'|| H.DV) AS "2_RUT_H",
                                  H.NOMBRE  AS "3", H.APELLIDO_P AS "4", H.APELLIDO_M  AS "5", H.ESTADO  AS "6"
                                FROM HUESPED H 
                                INNER JOIN CLIENTE C ON H.ID_CLIENTE = C.ID_CLIENTE WHERE C.ID_CLIENTE = %s""", [idCliente])
                huespedes_list = cursor.fetchall()

            else:
                cursor.execute("""SELECT H.ID_HUESPED, (C.RUT_EMPRESA ||'-'|| C.DV) RUT_E, (H.RUT ||'-'|| H.DV) AS RUT_H,
                                  H.NOMBRE, H.APELLIDO_P, H.APELLIDO_M, H.ESTADO
                                FROM HUESPED H 
                                INNER JOIN CLIENTE C ON H.ID_CLIENTE = C.ID_CLIENTE""")
                huespedes_list = cursor.fetchall()
        except Exception as e:
            print(e)
            pass

    data = {
        'huespedes': huespedes_list
    }

    return render(request, 'Clientes/huespedes.html', data)


def nuevo_huesped(request):
    cliente_m = None
    clientes_list = None
    idTipoCliente = ''
    with connection.cursor() as cursor:
        try:
            if request.user.is_cliente:
                cursor.execute("SELECT ID_CLIENTE, RUT_EMPRESA, DV FROM CLIENTE WHERE ID_USUARIO = %s and ESTATUS = %s", [
                               request.user.id, 1])
                cliente = cursor.fetchone()

                cliente_m = Cliente()
                cliente_m.id = cliente[0]
                cliente_m.rut_empresa = cliente[1]
                cliente_m.dv = cliente[2]
            else:
                cursor.execute("SELECT ID_TIPO_CLIENTE FROM TIPO_CLIENTE WHERE DESCRIPCION LIKE 'Cliente' ")
                idTipoCliente = cursor.fetchone()[0]
                cursor.execute(f"SELECT ID_CLIENTE, RUT_EMPRESA, DV FROM CLIENTE WHERE ID_TIPO_CLIENTE = {idTipoCliente} and ESTATUS = 1")
                clientes = cursor.fetchall()
                print(clientes)
                clientes_list = []

                for cliente in clientes:
                    cliente_m = Cliente()
                    cliente_m.id = cliente[0]
                    cliente_m.rut_empresa = cliente[1]
                    cliente_m.dv = cliente[2]

                    clientes_list.append(cliente_m)
        except Exception as e:
            print(e)
            pass

    data = {
        'cliente_m': cliente_m,
        'clientes': clientes_list
    }

    if request.method == "POST":
        rut_empresa = None

        if request.user.is_cliente:
            rut_empresa = str(cliente_m.rut_empresa) + cliente_m.dv
        else:
            rut_empresa = request.POST.get('rut_emp', None)

        rut_emp = rut_empresa
        rut_emp = rut_emp.replace('.', '')
        rut_emp = rut_emp.replace('-', '')
        rut_emp = rut_emp.rstrip(rut_emp[-1])
        dv_emp = rut_empresa[-1]

        rut_hues = request.POST['rut']
        rut_hues = rut_hues.replace('.', '')
        rut_hues = rut_hues.replace('-', '')
        rut_hues = rut_hues.rstrip(rut_hues[-1])
        dv_hues = request.POST['rut'][-1]

        nombres = request.POST['nombres']
        a_paterno = request.POST['apellido_p']
        a_materno = request.POST['apellido_m']
        estado = request.POST['estado']
        email = request.POST['email']
        telefono = request.POST['telefono']
        fec_nacimiento = request.POST['fec-nac']

        nombres = nombres.strip().lower()
        a_paterno = a_paterno.strip().lower()
        a_materno = a_materno.strip().lower()
        email = email.strip().lower()

        print(fec_nacimiento)

        if len(nombres) > 0 and len(a_paterno) > 0 and len(a_materno) > 0:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        "SELECT ID_CLIENTE FROM CLIENTE WHERE RUT_EMPRESA = %s", [rut_emp])
                    cliente = cursor.fetchone()

                    cursor.execute(f"""
                                 SELECT COUNT(*) AS TT 
                                    FROM HUESPED H 
                                    JOIN CLIENTE C ON H.ID_CLIENTE = C.ID_CLIENTE 
                                    WHERE C.RUT_EMPRESA = '{rut_emp}' AND RUT = '{rut_hues}'
                                   """)
                    valrut = cursor.fetchone()

                    if valrut[0] > 0:
                        messages.error(request, 'El Rut Ingresado ya Existe')
                    else:

                        cursor.execute("INSERT INTO HUESPED (RUT, DV, NOMBRE, APELLIDO_P, APELLIDO_M, EMAIL, TELEFONO, "
                                       "FECHA_NACIMIENTO, ESTADO, ID_CLIENTE) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                       [rut_hues, dv_hues, nombres, a_paterno, a_materno, email, telefono, fec_nacimiento, estado, cliente[0]])

                        messages.success(
                            request, 'El Huésped se ha Creado Correctamente')
                        return redirect('huesped-new')
                except Exception as e:
                    print(e)
                    pass

    return render(request, 'Clientes/huesped-new.html', data)


def edit_huesped(request, id):
    edit = 'editado'
    fnac = ''

    with connection.cursor() as cursor:
        try:
            cursor.execute(f"""SELECT H.ID_CLIENTE, (C.RUT_EMPRESA ||'-'|| C.DV) RUT_E, (H.RUT ||'-'|| H.DV) AS RUT_H,
                                  H.NOMBRE, H.APELLIDO_P, H.APELLIDO_M, H.ESTADO, H.EMAIL, H.TELEFONO, H.FECHA_NACIMIENTO
                                FROM HUESPED H 
                                INNER JOIN CLIENTE C ON H.ID_CLIENTE = C.ID_CLIENTE WHERE H.ID_HUESPED = {id}
                            """)
            huesped = cursor.fetchone()
            formato = '%Y-%m-%d'
            if huesped[9]:
                fnac = huesped[9].strftime(formato)

        except Exception as e:
            messages.error(
                request, 'El Huésped que desea editar No Existe o fue eliminado')
            return redirect('huespedes-list')

    if request.method == "POST":
        nombres = request.POST['nombres']
        a_paterno = request.POST['apellido_p']
        a_materno = request.POST['apellido_m']
        estado = request.POST['estado']
        email = request.POST['email']
        telefono = request.POST['telefono']
        fec_nac = request.POST['fec-nac']

        rut_hues = request.POST['rut']
        rut_hues = rut_hues.replace('.', '')
        rut_hues = rut_hues.replace('-', '')
        rut_hues = rut_hues.rstrip(rut_hues[-1])
        dv_hues = request.POST['rut'][-1]

        nombres = nombres.strip().lower()
        a_paterno = a_paterno.strip().lower()
        a_materno = a_materno.strip().lower()
        email = email.strip().lower()
        if len(nombres) > 0 and len(a_paterno) > 0 and len(a_materno) > 0 and len(email) > 0:
            with connection.cursor() as cursor:
                try:
                    cursor.execute("UPDATE HUESPED SET RUT = %s, DV = %s, NOMBRE = %s, APELLIDO_P = %s, "
                                   "APELLIDO_M = %s, EMAIL = %s, TELEFONO = %s, FECHA_NACIMIENTO = %s, ESTADO = %s WHERE ID_HUESPED = %s",
                                   [rut_hues, dv_hues, nombres, a_paterno, a_materno, email, telefono, fec_nac, estado, id])

                    messages.success(
                        request, 'Huesped modificado correctamente')
                    return redirect('huespedes-list')
                except Exception as e:
                    print(e)
                    pass
        else:
            messages.error(
                request, f'Revise Campos Obligatorios. Completelos para Continuar')
    data = {
        'edit': edit,
        'huesped': huesped,
        'fnac': fnac
    }
    return render(request, 'Clientes/huesped-edit.html', data)


def eliminar_huesped(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "UPDATE HUESPED SET ESTADO = %s WHERE id_HUESPED = %s", [0, id])
        except Exception as e:
            print(e)
            pass

    messages.success(request, "Eliminado correctamente")
    return redirect(to="huespedes-list")


@csrf_exempt
def huesped_carga(request):
    #template = loader.get_template('export/importar.html')
    mensaje = ''
    clientes = ''
    clienteid = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT ID_TIPO_CLIENTE FROM TIPO_CLIENTE WHERE DESCRIPCION LIKE 'Cliente' ")
            idTipoCliente = cursor.fetchone()[0]            
            cursor.execute(
                f"SELECT ID_CLIENTE, (RUT_EMPRESA ||'-'|| DV) AS RUT, RAZON_SOCIAL FROM CLIENTE WHERE ID_TIPO_CLIENTE = {idTipoCliente} AND ESTATUS = 1")
            clientes = cursor.fetchall()
        except Exception as e:
            print(e)
            pass
    if request.method == 'POST':
        try:
            clienteid = request.POST['clienteid']
        except:
            pass
        huesped_resource = HuespedResource()
        dataset = Dataset()
        print(dataset)
        try:
            nuevos_huespedes = request.FILES['xlsfile']
            print(nuevos_huespedes)
            imported_data = dataset.load(nuevos_huespedes.read())
            for data in imported_data:
                print(data)

                if data == '':
                    mensaje = 'nofile'
                    messages.error(
                        request, ' No se ha seleccionado archivo, Este posee un Formato Inválido o Viene Vacio')
                else:
                    huesped = Huesped()
                    huesped.rut = data[1]
                    huesped.dv = data[2]
                    huesped.nombre = data[3]
                    huesped.apellido_p = data[4]
                    huesped.apellido_m = data[5]
                    huesped.email = data[6]
                    huesped.telefono = data[7]
                    huesped.fecha_nacimiento = data[8]
                    if huesped.fecha_nacimiento == None:
                        huesped.fecha_nacimiento = ''
                    else:
                        huesped.fecha_nacimiento = data[8]
                    print(clienteid)
                    print( huesped.fecha_nacimiento)

                    with connection.cursor() as cursor:
                        try:
                            if len(clienteid) < 1:
                                print('if')
                                cursor.execute("SELECT ID_CLIENTE FROM CLIENTE WHERE ID_USUARIO = %s", [
                                    request.user.id])
                                cliente_db = cursor.fetchone()
                                cursor.execute(
                                    f"SELECT COUNT(*) TT FROM HUESPED WHERE RUT = '{huesped.rut}' AND ID_CLIENTE = {cliente_db[0]}")
                                validaRut = cursor.fetchone()
                                if validaRut[0] > 0:
                                    messages.error(
                                        request, 'Existe uno o más Huésped ya Ingresado(s)!!')
                                    pass
                                else:
                                    cursor.execute("INSERT INTO HUESPED (RUT, DV, NOMBRE, APELLIDO_P, "
                                                   "APELLIDO_M, EMAIL, TELEFONO, FECHA_NACIMIENTO, ID_CLIENTE, ESTADO) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                                   [huesped.rut, huesped.dv, huesped.nombre, huesped.apellido_p, huesped.apellido_m, huesped.email, huesped.telefono, huesped.fecha_nacimiento, cliente_db[0], 1])
                                    mensaje = 'ok'
                                    messages.success(
                                        request, 'Carga Realizada Correctamente')
                            else:
                                print('else')
                                cursor.execute(
                                    f"SELECT COUNT(*) TT FROM HUESPED WHERE RUT = '{huesped.rut}' AND ID_CLIENTE = {clienteid}")
                                validaRut = cursor.fetchone()
                                if validaRut[0] > 0:
                                    messages.error(
                                        request, 'Existe uno o más Huésped ya Ingresado(s)!!')
                                    pass
                                else:
                                    cursor.execute(f""" 
                                                INSERT INTO HUESPED (RUT, DV, NOMBRE, APELLIDO_P, APELLIDO_M, EMAIL, TELEFONO, FECHA_NACIMIENTO, ID_CLIENTE, ESTADO)
                                                
                                                VALUES ('{huesped.rut}','{huesped.dv}', '{huesped.nombre}','{huesped.apellido_p}','{huesped.apellido_m}', '{huesped.email}',
                                                '{huesped.telefono}', '{huesped.fecha_nacimiento}', '{clienteid}',1)
                                                """)
                                    messages.success(
                                        request, 'Carga Realizada Correctamente')
                        except Exception as e:
                            print(e)
                            messages.error(
                                request, 'No se pudo realizar la carga. Verifique Archivo e Intente Nuevamente')
                            pass

        except:
            mensaje = 'nofile'
            messages.error(
                request, ' No se ha seleccionado archivo, Este posee un Formato Inválido o Viene Vacio')
    data = {
        'mensaje': mensaje,
        'clientes': clientes
    }
    return render(request, 'Clientes/export/huespedes-carga.html', data)

# ***Módulo:Empleados*** Opción: servicios habitaciones


def nueva_habitacion(request):
    imagen = ''
    nom = ''
    tipos_hab_list = ''
    estados_list = ''
     
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "SELECT ID_TIPO_HABITACION, DESCRIPCION FROM TIPO_HABITACION WHERE ESTADO = %s", [1])
            tipos_habitacion_db = cursor.fetchall()
            tipos_hab_list = []

            for tipo_habitacion in tipos_habitacion_db:
                tipo_hab_m = TipoHabitacion()
                tipo_hab_m.id = tipo_habitacion[0]
                tipo_hab_m.descripcion = tipo_habitacion[1]

                tipos_hab_list.append(tipo_hab_m)

            cursor.execute("SELECT ID_ESTADO_HABITACION, DESCRIPCION FROM ESTADO_HABITACION")
            estados_hab_db = cursor.fetchall()
            estados_list = []

            for estado in estados_hab_db:
                estado_m = EstadoHabitacion()
                estado_m.id = estado[0]
                estado_m.descripcion = estado[1]

                estados_list.append(estado_m)
        except Exception as e:
            print(e)
            pass
        print(estados_list)
    data = {
        'tipos_habitaciones': tipos_hab_list,
        'estados': estados_list
    }

    if request.method == "POST":
        tipo_habitacion = request.POST['tip_hab']
        nro_habitacion = request.POST['nro_hab']
        precio = request.POST['precio']
        disponibilidad = request.POST.get('disp_sel', None)
        estado = request.POST.get('estado', None)
        muestra_menu = request.POST.get('mues_sel', None)
        descripcion = request.POST['descripcion']
        try:
            if request.FILES['imagen']:
                imagen = request.FILES['imagen']
                nom = imagen.name
                fs = FileSystemStorage(location='media/Habitaciones/')
                if os.path.isfile(f'media/Habitaciones/{nom}'):
                    print('existe')
                    os.remove(f'media/Habitaciones/{nom}')
                    filename = fs.save(imagen.name, imagen)
                    uploaded_file_url = fs.url(filename)
                else:
                    print('no existe')
                    filename = fs.save(imagen.name, imagen)
                    uploaded_file_url = fs.url(filename)
        except:
            pass
            print('me cai')
        print('imprime foto', imagen)
        nro_habitacion = nro_habitacion.strip()
        precio = precio.strip()
        descripcion = descripcion.strip()
        if len(nom) > 100:
            messages.error(
                request, f'Nombre de Imagen excede el Largo Máximo Permitido de 100 Caracteres, Modifique o elija otra para Continuar')
        else:
            print(nom)
            if (len(nro_habitacion) > 0 and nro_habitacion.isnumeric()) and (len(precio) > 0 and precio.isnumeric()) and len(descripcion) > 0:
                with connection.cursor() as cursor:
                    try:

                        cursor.execute(
                            f"""SELECT COUNT(*) AS TT  FROM HABITACION WHERE NUMERO_HABITACION = '{nro_habitacion}'""")
                        valHabitacion = cursor.fetchone()
                        if valHabitacion[0] > 0:
                            messages.error(
                                request, f'La Habitación N° {nro_habitacion} Ya Existe')
                        else:
                            cursor.execute("INSERT INTO HABITACION(ID_TIPO_HABITACION, NUMERO_HABITACION, PRECIO, "
                                           "ID_ESTADO_HABITACION, ESTADO, MUESTRA_MENU, DESCRIPCION, IMAGEN) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                                           [tipo_habitacion, nro_habitacion, precio, disponibilidad, estado, muestra_menu, descripcion, nom])

                            messages.success(
                                request, 'Habitación agregada correctamente')
                            return redirect('habitacion-new')
                    except Exception as e:
                        print(e)
                        pass
            else:
                messages.error(
                    request, f'Revise Campos Obligatorios. Completelos para Continuar')

    return render(request, 'Empleados/Servicios/Habitacion/habitacion.html', data)


def edit_habitacion(request, id):
    imagen = ''
    nom = ''
    uploaded_file_url = ''
    tipos_hab_list = ''
    habitacion_db = ''
    estados_list = ''
    habitacion_m = ''
    tipos_habitacion_db = ''
    tipo_habitacion = ''
    estados_hab_db = ''
    estado_habitacion = ''
    with connection.cursor() as cursor:
        try:

           
            #HABITACIÓN A MODIFICAR
            cursor.execute(f"""SELECT ID_HABITACION AS "0", NUMERO_HABITACION AS "1", PRECIO AS "2", DESCRIPCION AS "3", 
                           ID_ESTADO_HABITACION  AS "4", 
                           ID_TIPO_HABITACION AS "5", ESTADO AS "6", MUESTRA_MENU AS "7", IMAGEN  AS "8"
                           FROM HABITACION WHERE ID_HABITACION ={id}""")
            habitacion_db = cursor.fetchone()

            cursor.execute("SELECT * FROM TIPO_HABITACION WHERE ESTADO = 1")
            tipos_habitacion_db = cursor.fetchall()

            cursor.execute("SELECT * FROM ESTADO_HABITACION")
            estados_hab_db = cursor.fetchall()


            if habitacion_db[5] is not None:
                cursor.execute(
                    "SELECT * FROM TIPO_HABITACION WHERE ID_TIPO_HABITACION = %s", [habitacion_db[5]])
                tipo_habitacion = cursor.fetchone()
            if habitacion_db[4] is not None:
                cursor.execute(
                    "SELECT * FROM ESTADO_HABITACION WHERE ID_ESTADO_HABITACION = %s", [habitacion_db[4]])
                estado_habitacion = cursor.fetchone()


        except Exception as e:
            print(e)
            pass

    if request.method == "POST":
        tipo_habitacion = request.POST['tip-hab']
        precio = request.POST['precio']
        disponibilidad = request.POST.get('disp_sel', None)
        estado = request.POST.get('estado', None)
        muestra_menu = request.POST.get('mues_sel', None)
        descripcion = request.POST['descripcion']
        try:
            if request.FILES['image']:
                print(' hay imagen')
                imagen = request.FILES['image']
                nom = imagen.name
                print(nom)
                fs = FileSystemStorage(location='media/Habitaciones/')
                if nom != habitacion_db[8]:
                    if os.path.isfile(f'media/Habitaciones/{nom}'):
                        print('existe')
                        os.remove(f'media/Habitaciones/{habitacion_db[8]}')
                        filename = fs.save(nom, imagen)
                        uploaded_file_url = fs.url(filename)
                    else:
                        print('no existe')
                        filename = fs.save(nom, imagen)
                        uploaded_file_url = fs.url(filename)
                else:
                    if os.path.isfile(f'media/Habitaciones/{habitacion_db[8]}'):
                        print('existe')
                        os.remove(f'media/Habitaciones/{habitacion_db[8]}')
                        filename = fs.save(imagen.name, imagen)
                        uploaded_file_url = fs.url(filename)
                    else:
                        print('no existe')
                        filename = fs.save(imagen.name, imagen)
                        uploaded_file_url = fs.url(filename)
        except Exception as e:
            nom = habitacion_db[8]
            pass
        print(nom)
        precio = precio.strip()
        descripcion = descripcion.strip()
        if len(nom) > 100:
            messages.error(
                request, f'Nombre de Imagen excede el Largo Máximo Permitido de 100 Caracteres, Modifique o elija otra para Continuar')
        else:
            if len(precio) > 0 and precio.isnumeric() and len(descripcion) > 0:
                with connection.cursor() as cursor:
                    try:
                        cursor.execute("UPDATE HABITACION SET ID_TIPO_HABITACION = %s,  "
                                       "PRECIO = %s, ID_ESTADO_HABITACION = %s, ESTADO = %s, MUESTRA_MENU = %s, DESCRIPCION = %s, IMAGEN = %s "
                                       "WHERE ID_HABITACION = %s", [tipo_habitacion,  precio, disponibilidad, estado, muestra_menu, descripcion, nom, id])

                        messages.success(
                            request, 'Habitación modificada correctamente')
                        return redirect('habitaciones-list')
                    except Exception as e:
                        print(e)
                        pass
            else:
                messages.error(
                    request, f'Revise Campos Obligatorios. Completelos para Continuar')
    print(estados_list)
    data = {
        'habitacion_db': habitacion_db,
        'tipos_habitaciones': tipos_habitacion_db,
        'estados': estados_hab_db,
        'tipo_habitacion':tipo_habitacion,
        'estado_habitacion': estado_habitacion,
        'uploaded_file_url': uploaded_file_url,
    }
    return render(request, 'Empleados/Servicios/Habitacion/edit_habitacion.html', data)


def elim_habitacion(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "UPDATE HABITACION SET ESTADO = %s WHERE ID_HABITACION = %s", [0, id])
            messages.success(request, 'Habitación eliminada')
        except Exception as e:
            print(e)
            pass

    return redirect('habitaciones-list')


def habitaciones(request):
    habitaciones_list =''
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                """
            SELECT H.ID_HABITACION, H.NUMERO_HABITACION, H.PRECIO, H.ESTADO, H.IMAGEN, H.MUESTRA_MENU, EH.ID_ESTADO_HABITACION,
            EH.DESCRIPCION, TH.ID_TIPO_HABITACION, TH.DESCRIPCION
            FROM HABITACION H
            JOIN ESTADO_HABITACION EH ON H.ID_ESTADO_HABITACION = EH.ID_ESTADO_HABITACION
            JOIN TIPO_HABITACION TH ON H.ID_TIPO_HABITACION = TH.ID_TIPO_HABITACION
            """)
            habitaciones_list = cursor.fetchall()
        except Exception as e:
            print(e)
            pass

    data = {
        'habitaciones': habitaciones_list
    }

    return render(request, 'Empleados/Servicios/Habitacion/habitaciones.html', data)


def tipo_habitacion(request):
    tipo_habitaciones = ''
    accesorios =''
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "SELECT ID_TIPO_HABITACION, DESCRIPCION, ESTADO, CAPACIDAD FROM TIPO_HABITACION ")
            tipo_habitacion_db = cursor.fetchall()
            tipo_habitaciones = []

            for tipo_habitacion in tipo_habitacion_db:
                tipo_habitacion_m = TipoHabitacion()
                tipo_habitacion_m.id = tipo_habitacion[0]
                tipo_habitacion_m.descripcion = tipo_habitacion[1]
                tipo_habitacion_m.estado = tipo_habitacion[2]
                tipo_habitacion_m.capacidad = tipo_habitacion[3]

                tipo_habitaciones.append(tipo_habitacion_m)

            cursor.execute(
                "SELECT ID_ACCESORIO, DESCRIPCION FROM ACCESORIO WHERE ESTATUS = %s", [1])
            accesorios_db = cursor.fetchall()
            accesorios = []

            for accesorio in accesorios_db:
                accesorio_m = Accesorio()
                accesorio_m.id = accesorio[0]
                accesorio_m.descripcion = accesorio[1]

                accesorios.append(accesorio_m)

        except Exception as e:
            print(e)
            pass
    print(tipo_habitaciones)
    data = {
        'tipos_habitaciones': tipo_habitaciones,
        'accesorios': accesorios
    }

    if request.method == "POST":
        nombre = request.POST['nombre-tiphab']
        capacidad = request.POST['capacidad']
        estatus = request.POST.get('est-sel', None)
        accesorios_r = request.POST.getlist('accesorios-sel')

        nombre = nombre.strip()
        if len(nombre) > 0 and len(estatus) > 0 and len(accesorios_r) >= 0 and len(capacidad) > 0:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        "SELECT COUNT(*)TT FROM TIPO_HABITACION WHERE DESCRIPCION LIKE %s", [nombre])
                    validaExistencia = cursor.fetchone()
                    if validaExistencia[0] < 1:
                        cursor.execute("INSERT INTO TIPO_HABITACION (DESCRIPCION, ESTADO, CAPACIDAD) VALUES (%s, %s, %s)", [
                            nombre, estatus, capacidad])
                        cursor.execute(
                            "SELECT ID_TIPO_HABITACION FROM TIPO_HABITACION WHERE DESCRIPCION = %s", [nombre])
                        tipo_habitacion = cursor.fetchone()[0]

                        for accesorio in accesorios_r:
                            cursor.execute("INSERT INTO HABITACION_ACCESORIO (ID_ACCESORIO, ID_TIPO_HABITACION) VALUES (%s, %s)", [
                                accesorio, tipo_habitacion])

                        messages.success(
                            request, 'Tipo de habitación registrado correctamente')
                    else:
                        messages.error(
                            request, 'El Tipo de Habitación ya Existe')
                    return redirect('tipo-habitacion')
                except Exception as e:
                    print(e)
                    pass
        else:
            messages.error(
                request, 'Complete los Campos Obligatorios para Continuar, estos se identifican con (*)')
    return render(request, 'Empleados/Servicios/Habitacion/tipo_habitacion.html', data)


def edit_tipo_hab(request, id):
    accesorios = []
    accesorios_list = []
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "SELECT DESCRIPCION, ESTADO, CAPACIDAD FROM TIPO_HABITACION WHERE ID_TIPO_HABITACION = %s", [id])
            tipo_hab_db = cursor.fetchone()
            if not tipo_hab_db:
                messages.error(
                    request, 'El Tipo de Habitación que desea editar No Existe o fue eliminado')
                return redirect('tipo-habitacion')
            tipo_habitacion = TipoHabitacion()
            tipo_habitacion.id = id
            tipo_habitacion.descripcion = tipo_hab_db[0]
            tipo_habitacion.estado = tipo_hab_db[1]
            tipo_habitacion.capacidad = tipo_hab_db[2]
            print(tipo_habitacion)

            cursor.execute(
                "SELECT ID_ACCESORIO FROM HABITACION_ACCESORIO WHERE ID_TIPO_HABITACION = %s", [id])
            accesorios_hab_db = cursor.fetchall()
            accesorios = []

            for accesorio in accesorios_hab_db:
                cursor.execute(
                    "SELECT ID_ACCESORIO, DESCRIPCION FROM ACCESORIO WHERE ID_ACCESORIO = %s", [accesorio[0]])
                accesorios_db = cursor.fetchone()
                print(accesorios_db)

                accesorio_m = Accesorio()
                accesorio_m.id = accesorios_db[0]
                accesorio_m.descripcion = accesorios_db[1]

                accesorios.append(accesorio_m)

            cursor.execute("SELECT ID_ACCESORIO, DESCRIPCION FROM ACCESORIO")
            accesorios_db_list = cursor.fetchall()
            accesorios_list = []

            for accesorio in accesorios_db_list:
                accesorio_m = Accesorio()
                accesorio_m.id = accesorio[0]
                accesorio_m.descripcion = accesorio[1]

                accesorios_list.append(accesorio_m)

        except Exception as e:
            print(e)
            pass

    data = {
        'tipo_habitacion': tipo_habitacion,
        'accesorios_tip_hab': accesorios,
        'accesorios_list': accesorios_list
    }

    if request.method == 'POST':
        tipo_habitacion = request.POST['nombre-tip-hab']
        estatus = request.POST.get('est-sel', None)
        capacidad = request.POST['capacidad']
        accesorios_r = request.POST.getlist('accesorios')
        print(accesorios_r)
        tipo_habitacion = tipo_habitacion.strip()

        if len(tipo_habitacion) > 0 and len(estatus) > 0 and len(accesorios_r) >= 0 and len(capacidad) > 0:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        "SELECT COUNT(*)TT FROM TIPO_HABITACION WHERE DESCRIPCION LIKE %s and ID_TIPO_HABITACION != %s", [tipo_habitacion, id])
                    validaExistencia = cursor.fetchone()
                    if validaExistencia[0] > 0:
                        messages.error(
                            request, 'El Tipo de Habitación ya Existe')
                    else:
                        cursor.execute("UPDATE TIPO_HABITACION SET DESCRIPCION = %s, ESTADO = %s, CAPACIDAD = %s WHERE ID_TIPO_HABITACION = %s", [
                            tipo_habitacion, estatus, capacidad, id])

                        cursor.execute(
                            "DELETE FROM HABITACION_ACCESORIO WHERE ID_TIPO_HABITACION = %s", [id])

                        for accesorio in accesorios_r:
                            cursor.execute(
                                "INSERT INTO HABITACION_ACCESORIO (ID_ACCESORIO, ID_TIPO_HABITACION) VALUES (%s, %s)", [accesorio, id])

                        messages.success(
                            request, 'Tipo de habitación modificado')
                        return redirect('tipo-habitacion')

                except Exception as e:
                    print(e)
                    pass
        else:
            messages.error(
                request, 'Complete los Campos Obligatorios para Continuar, estos se identifican con (*)')

    return render(request, 'Empleados/Servicios/Habitacion/edit_tipo_hab.html', data)


def elim_tipo_hab(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "UPDATE TIPO_HABITACION SET ESTADO = %s WHERE ID_TIPO_HABITACION = %s", [0, id])
            messages.success(
                request, 'Tipo de Habitación eliminada correctamente')
        except Exception as e:
            print(e)
            pass

    return redirect('tipo-habitacion')


def accesorios(request):
    accesorios = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "SELECT ID_ACCESORIO, DESCRIPCION, ESTATUS FROM ACCESORIO")
            accesorios_db = cursor.fetchall()
            accesorios = []

            for accesorio in accesorios_db:
                accesorios_m = Accesorio()
                accesorios_m.id = accesorio[0]
                accesorios_m.descripcion = accesorio[1]
                accesorios_m.estatus = accesorio[2]

                accesorios.append(accesorios_m)
        except Exception as e:
            print(e)

    data = {
        'accesorios': accesorios
    }

    if request.method == "POST":
        nombre = request.POST['nombre-acces']
        estatus = request.POST.get('est-sel', None)

        nombre = nombre.strip()

        if len(nombre) > 0:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        "SELECT COUNT(*)TT FROM ACCESORIO WHERE DESCRIPCION LIKE %s  ", [nombre])
                    validaExistencia = cursor.fetchone()
                    if validaExistencia[0] > 0:
                        messages.error(request, 'El Accesorio ya Existe')
                    else:
                        cursor.execute("INSERT INTO ACCESORIO (DESCRIPCION, ESTATUS) VALUES(%s, %s)", [
                            nombre, estatus])
                        messages.success(
                            request, 'Accesorio registrado correctamente')
                        return redirect('accesorios-new')
                except Exception as e:
                    print(e)
                    pass
        else:
            messages.error(
                request, 'Complete los Campos Obligatorios para Continuar, estos se identifican con (*)')

    return render(request, 'Empleados/Servicios/Habitacion/accesorios.html', data)


def edit_accesorios(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "SELECT DESCRIPCION, ESTATUS FROM ACCESORIO WHERE ID_ACCESORIO = %s", [id])
            accesorio_db = cursor.fetchone()

            accesorio = Accesorio()
            accesorio.id = id
            accesorio.descripcion = accesorio_db[0]
            accesorio.estatus = accesorio_db[1]
        except Exception as e:
            print(e)
            messages.error(
                request, 'El Accesorio que desea editar No Existe o fue eliminado')
            return redirect('accesorios-new')

    data = {
        'accesorio': accesorio
    }

    if request.method == 'POST':
        descripcion = request.POST['nombre-acces']
        estatus = request.POST.get('acces-sel', None)

        descripcion = descripcion.strip()

        if len(descripcion) > 0:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        "SELECT COUNT(*)TT FROM ACCESORIO WHERE DESCRIPCION LIKE %s and ID_ACCESORIO != %s", [descripcion, id])
                    validaExistencia = cursor.fetchone()
                    if validaExistencia[0] > 0:
                        messages.error(request, 'El Accesorio ya Existe')
                    else:
                        cursor.execute("UPDATE ACCESORIO SET DESCRIPCION = %s, ESTATUS = %s WHERE ID_ACCESORIO = %s", [
                            descripcion, estatus, id])
                        messages.success(request, 'Accesorio modificado')

                        return redirect('accesorios-new')
                except Exception as e:
                    print(e)
                    pass
        else:
            messages.error(
                request, 'Complete los Campos Obligatorios para Continuar, estos se identifican con (*)')

    return render(request, 'Empleados/Servicios/Habitacion/edit_accesorio.html', data)


def eliminar_accesorios(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "UPDATE ACCESORIO SET ESTATUS = %s WHERE ID_ACCESORIO = %s", [0, id])
        except Exception as e:
            print(e)
            pass

    return redirect('accesorios-new')

# ***Módulo:Empleados*** Opción: servicios comedor


def nuevo_plato(request):
    imagen = ''
    nom = ''
    comedores = ''
    uploaded_file_url = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                """SELECT * FROM TIPO_COMEDOR WHERE ESTADO = 1 """)
            comedores = cursor.fetchall()

        except Exception as e:
            print(e)
            pass
    if request.method == "POST":
        comedor = request.POST['comedor']
        nombre_plato = request.POST['nombreplato']
        estado = request.POST['estado']
        fdesde = request.POST['fdesde']
        fhasta = request.POST['fhasta']
        try:
            if request.FILES['imagen']:
                imagen = request.FILES['imagen']
                nom = imagen.name
                fs = FileSystemStorage(location='media/imgPlatos/')
                if os.path.isfile(f'media/imgPlatos/{nom}'):
                    print('existe')
                    os.remove(f'media/imgPlatos/{nom}')
                    filename = fs.save(imagen.name, imagen)
                    uploaded_file_url = fs.url(filename)
                else:
                    print('no existe')
                    filename = fs.save(imagen.name, imagen)
                    uploaded_file_url = fs.url(filename)
        except:
            pass
        comedor = comedor.strip()
        nombre_plato = nombre_plato.strip()
        estado = estado.strip()
        fdesde = fdesde.strip()
        fhasta = fhasta.strip()
        if fdesde > fhasta:
            messages.error(
                request, f'La Fecha de Inicio NO puede ser mayor a la de Termino. Modifique para Continuar')
        else:
            if len(nom) > 100:
                messages.error(
                    request, f'Nombre de Imagen excede el Largo Máximo Permitido de 100 Caracteres, Modifique o elija otra para Continuar')
            else:
                if len(comedor) > 0 and len(nombre_plato) > 0 and len(fdesde) > 0 and len(fhasta) > 0 and len(imagen) >= 0:
                    with connection.cursor() as cursor:
                        try:
                            cursor.execute(
                                "SELECT COUNT(*)TT FROM PLATO_SEMANAL WHERE DESCRIPCION LIKE %s", [nombre_plato])
                            validaExistencia = cursor.fetchone()
                            if validaExistencia[0] > 0:
                                messages.error(
                                    request, 'El Plato Ingresado ya Existe')
                            else:
                                cursor.execute(f"""
                                                    INSERT INTO PLATO_SEMANAL (DESCRIPCION, DIA_DESDE, DIA_HASTA, IMAGEN,ID_TIPO_COMEDOR, ESTADO) 
                                                                VALUES ('{nombre_plato}', '{fdesde}', '{fhasta}','{nom}', '{comedor}', {estado})
                                                    """)

                                messages.success(
                                    request, f' {nombre_plato} Agregado como Plato correctamente')
                                return redirect('platos-list')
                        except Exception as e:
                            print(e)
                            pass
                else:
                    messages.error(
                        request, f'Revise Campos Obligatorios. Completelos para Continuar')

    data = {
        'comedores': comedores,
        'uploaded_file_url': uploaded_file_url
    }

    return render(request, 'Empleados/Servicios/Comedor/plato.html', data)


def edit_plato(request, id):
    imagen = ''
    nom = ''
    uploaded_file_url = ''
    comedor = ''
    fI = ''
    fT = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                f"""SELECT ID_COMEDOR, DESCRIPCION, DIA_DESDE, DIA_HASTA, IMAGEN, ID_TIPO_COMEDOR, ESTADO FROM PLATO_SEMANAL WHERE ID_COMEDOR = {id}""")
            plato_edit = cursor.fetchone()

            cursor.execute(
                """SELECT * FROM TIPO_COMEDOR WHERE ESTADO = 1 """)
            comedores = cursor.fetchall()

            cursor.execute(
                "SELECT * FROM TIPO_COMEDOR WHERE ID_TIPO_COMEDOR = %s", [plato_edit[5]])
            comedor = cursor.fetchone()
            formato = '%Y-%m-%d'
            fI = plato_edit[2].strftime(formato)
            fT = plato_edit[3].strftime(formato)
        except Exception as e:
            print(e)
            messages.error(
                request, 'El Plato que desea editar No Existe o fue eliminado')
            return redirect('platos-list')

    if request.method == "POST":
        comedor = request.POST['comedor']
        nombre_plato = request.POST['nombreplato']
        estado = request.POST['estado']
        fdesde = request.POST['fdesde']
        fhasta = request.POST['fhasta']
        try:
            if request.FILES['imagen']:
                imagen = request.FILES['imagen']
                nom = imagen.name
                fs = FileSystemStorage(location='media/imgPlatos/')
                if nom != plato_edit[4]:
                    if os.path.isfile(f'media/imgPlatos/{nom}'):
                        print('existe')
                        os.remove(f'media/imgPlatos/{nom}')
                        filename = fs.save(imagen.name, imagen)
                        uploaded_file_url = fs.url(filename)
                    else:
                        print('no existe')
                        filename = fs.save(imagen.name, imagen)
                        uploaded_file_url = fs.url(filename)
                else:
                    if os.path.isfile(f'media/imgPlatos/{plato_edit[4]}'):
                        print('existe')
                        os.remove(f'media/imgPlatos/{plato_edit[4]}')
                        filename = fs.save(imagen.name, imagen)
                        uploaded_file_url = fs.url(filename)
                    else:
                        print('no existe')
                        filename = fs.save(imagen.name, imagen)
                        uploaded_file_url = fs.url(filename)
        except:
            nom = plato_edit[4]
            pass
        comedor = comedor.strip()
        nombre_plato = nombre_plato.strip()
        estado = estado.strip()
        fdesde = fdesde.strip()
        fhasta = fhasta.strip()
        if fdesde > fhasta:
            messages.error(
                request, f'La Fecha de Inicio NO puede ser mayor a la de Termino. Modifique para Continuar')
        else:
            if len(nom) > 100:
                messages.error(
                    request, f'Nombre de Imagen excede el Largo Máximo Permitido de 100 Caracteres, Modifique o elija otra para Continuar')
            else:
                if len(comedor) > 0 and len(nombre_plato) > 0 and len(fdesde) > 0 and len(fhasta) > 0 and len(imagen) >= 0:
                    with connection.cursor() as cursor:
                        try:
                            cursor.execute(
                                "SELECT COUNT(*)TT FROM PLATO_SEMANAL WHERE DESCRIPCION LIKE %s and ID_COMEDOR != %s", [nombre_plato, id])
                            validaExistencia = cursor.fetchone()
                            if validaExistencia[0] > 0:
                                messages.error(
                                    request, f'El Plato {nombre_plato} ya Existe')
                            else:
                                cursor.execute(f"""
                                                    UPDATE PLATO_SEMANAL SET DESCRIPCION = '{nombre_plato}', DIA_DESDE = '{fdesde}', DIA_HASTA = '{fhasta}',
                                                                                IMAGEN = '{nom}' ,ID_TIPO_COMEDOR = '{comedor}', ESTADO = {estado} 
                                                                                WHERE ID_COMEDOR = '{id}'
                                                    """)

                                messages.success(
                                    request, f' {nombre_plato} Modificado correctamente')
                                return redirect('platos-list')
                        except Exception as e:
                            print(e)
                            pass
                else:
                    messages.error(
                        request, f'Revise Campos Obligatorios. Completelos para Continuar')

    data = {
        'comedores': comedores,
        'uploaded_file_url': uploaded_file_url,
        'plato_edit': plato_edit,
        'comedor': comedor,
        'fI': fI,
        'fT': fT
    }

    return render(request, 'Empleados/Servicios/Comedor/edit-plato.html', data)


def eliminar_platos(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "UPDATE PLATO_SEMANAL SET ESTADO = %s WHERE ID_COMEDOR = %s", [0, id])
        except Exception as e:
            print(e)
            pass
    messages.success(request, "Eliminado correctamente")
    return redirect('platos-list')


def platos(request):
    platos = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                    SELECT P.ID_COMEDOR, P.DESCRIPCION, P.DIA_DESDE, P.DIA_HASTA, P.IMAGEN, P.ESTADO, TC.DESCRIPCION
                    FROM PLATO_SEMANAL P JOIN TIPO_COMEDOR TC ON P.ID_TIPO_COMEDOR = TC.ID_TIPO_COMEDOR
                """)
            platos = cursor.fetchall()

        except Exception as e:
            print(e)
            pass

    data = {
        'platos': platos
    }
    return render(request, 'Empleados/Servicios/Comedor/platos.html', data)


def tipo_comedor(request):
    nombre_tipo = ''
    estado = ''
    tipo_comedor = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute("""SELECT * FROM TIPO_COMEDOR """)
            tipo_comedor = cursor.fetchall()

        except Exception as e:
            print(e)
            pass
    if request.method == "POST":
        nombre_tipo = request.POST['comedor']
        estado = request.POST['estado']
        precio = request.POST['precio']
        if len(nombre_tipo) > 0 and len(estado) > 0 and len(precio) > 0:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        "SELECT COUNT(*)TT FROM TIPO_COMEDOR WHERE DESCRIPCION LIKE %s", [nombre_tipo])
                    validaExistencia = cursor.fetchone()
                    if validaExistencia[0] > 0:
                        messages.error(
                            request, f'El Nombre de Comedor {nombre_tipo} ya Existe')
                    else:
                        cursor.execute(
                            f"""INSERT INTO TIPO_COMEDOR (ESTADO, DESCRIPCION, PRECIO) VALUES ({estado}, '{nombre_tipo}',{precio})""")
                        messages.success(
                            request, f'Se ha registrado un Nuevo Tipo de Comedor con nombre {nombre_tipo}')
                        return redirect('tipo-comedor')
                except Exception as e:
                    print(e)
                    pass
        else:
            messages.error(
                request, f'Campo Nombre, Precio y Estado Obligatorios. Completelos para Continuar')
    data = {
        'tipo_comedor': tipo_comedor
    }

    return render(request, 'Empleados/Servicios/Comedor/tipo_comedor.html', data)


def edit_tipo_comedor(request, id):
    tipo_c = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"SELECT * FROM TIPO_COMEDOR WHERE ID_TIPO_COMEDOR = {id}")
            tipo_c = cursor.fetchone()
            if not tipo_c:
                messages.error(
                    request, 'El Tipo de Moneda que desea editar No Existe o fue eliminado')
                return redirect('tipo-comedor')
        except Exception as e:
            print(e)

    if request.method == "POST":
        nombre_tipo = request.POST['comedor']
        estado = request.POST['estado']
        precio = request.POST['precio']
        nombre_tipo = nombre_tipo.strip()
        if len(nombre_tipo) > 0 and len(estado) > 0 and len(precio) > 0:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        "SELECT COUNT(*)TT FROM TIPO_COMEDOR WHERE DESCRIPCION LIKE %s and id_TIPO_COMEDOR != %s", [nombre_tipo, id])
                    validaExistencia = cursor.fetchone()
                    if validaExistencia[0] > 0:
                        messages.error(
                            request, f'El Nombre de Comedor {nombre_tipo} ya Existe')
                    else:
                        cursor.execute(
                            f"""UPDATE TIPO_COMEDOR SET ESTADO = {estado}, DESCRIPCION='{nombre_tipo}', PRECIO = {precio} WHERE ID_TIPO_COMEDOR = {id} """)
                        messages.success(
                            request, f'Se ha Modificado el Tipo de Comedor con nombre {nombre_tipo} Correctamente')
                        return redirect('tipo-comedor')
                except Exception as e:
                    print(e)
                    pass
        else:
            messages.error(
                request, f'Campo Nombre, Precio y Estado Obligatorios. Completelos para Continuar')
    data = {
        'tipo_c': tipo_c,
    }
    return render(request, 'Empleados/Servicios/Comedor/edit_tipo_comedor.html', data)


def eliminar_tipo_comedor(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "UPDATE TIPO_COMEDOR SET ESTADO = %s WHERE ID_TIPO_COMEDOR = %s", [0, id])
        except Exception as e:
            print(e)
            pass
    messages.success(request, "Eliminado correctamente")
    return redirect('tipo-comedor')

# ***Módulo:Empleados*** Opción: servicios adicionales


def nuevo_servicio_ad(request):
    imagen = ''
    nom = ''
    uploaded_file_url = ''
    nombre = ''
    precio = ''
    descripcion = ''
    if request.method == "POST":
        nombre = request.POST['nombre']
        precio = request.POST['precio']
        muestra = request.POST['muestra']
        estado = request.POST['estado']
        descripcion = request.POST['descripcion']
        try:
            if request.FILES['imagen']:
                imagen = request.FILES['imagen']
                nom = imagen.name
                fs = FileSystemStorage(location='media/servAD/')
                if os.path.isfile(f'media/servAD/{nom}'):
                    print('existe')
                    os.remove(f'media/servAD/{nom}')
                    filename = fs.save(imagen.name, imagen)
                    uploaded_file_url = fs.url(filename)
                else:
                    print('no existe')
                    filename = fs.save(imagen.name, imagen)
                    uploaded_file_url = fs.url(filename)
        except:
            pass
        nombre = nombre.strip()
        estado = estado.strip()
        precio = precio.strip()
        muestra = muestra.strip()
        descripcion = descripcion.strip()

        if len(nom) > 100:
            messages.error(
                request, f'Nombre de Imagen excede el Largo Máximo Permitido de 100 Caracteres, Modifique o elija otra para Continuar')
        else:
            if len(nombre) > 0 and len(precio) > 0 and len(muestra) > 0 and len(estado) > 0 and len(descripcion) > 0 and len(imagen) >= 0:
                with connection.cursor() as cursor:
                    try:
                        cursor.execute(
                            "SELECT COUNT(*)TT FROM SERVICIO_ADICIONAL WHERE NOMBRE LIKE %s ", [nombre])
                        validaExistencia = cursor.fetchone()
                        if validaExistencia[0] > 0:
                            messages.error(
                                request, f'El Nombre de Servicio {nombre} ya Existe')
                        else:
                            cursor.execute(f"""
                                                INSERT INTO SERVICIO_ADICIONAL (NOMBRE, DESCRIPCION, PRECIO, MOSTRAR_INICIO, IMAGEN, ESTADO) 
                                                            VALUES ('{nombre}', '{descripcion}', '{precio}', '{muestra}','{nom}', {estado})
                                                """)

                            messages.success(
                                request, f' {nombre} Agregado como Servicio Adicional correctamente')
                            return redirect('servicios-list')
                    except Exception as e:
                        print(e)
                        pass
            else:
                messages.error(
                    request, f'Revise Campos Obligatorios. Completelos para Continuar')

    data = {
        'uploaded_file_url': uploaded_file_url,
        'nombre': nombre,
        'precio': precio,
        'descripcion': descripcion
    }

    return render(request, 'Empleados/Servicios/Adicional/servicio-ad.html', data)


def servicios_ad(request):
    servicios = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                    SELECT * FROM SERVICIO_ADICIONAL
                """)
            servicios = cursor.fetchall()

        except Exception as e:
            print(e)
            pass

    data = {
        'servicios': servicios
    }
    return render(request, 'Empleados/Servicios/Adicional/servicios-ad.html', data)


def edit_servicioad(request, id):
    imagen = ''
    nom = ''
    uploaded_file_url = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                f"""SELECT * FROM SERVICIO_ADICIONAL WHERE ID_SERVICIO = {id}""")
            servicio_edit = cursor.fetchone()
            if not servicio_edit:
                messages.error(
                    request, 'El Servicio Adicional que desea editar No Existe o fue eliminado')
                return redirect('servicios-list')

        except Exception as e:
            print(e)

    if request.method == "POST":
        nombre = request.POST['nombre']
        precio = request.POST['precio']
        muestra = request.POST['muestra']
        estado = request.POST['estado']
        descripcion = request.POST['descripcion']
        try:
            if request.FILES['imagen']:
                imagen = request.FILES['imagen']
                nom = imagen.name
                fs = FileSystemStorage(location='media/servAD/')
                if nom != servicio_edit[5]:
                    if os.path.isfile(f'media/servAD/{nom}'):
                        print('existe')
                        os.remove(f'media/servAD/{nom}')
                        filename = fs.save(imagen.name, imagen)
                        uploaded_file_url = fs.url(filename)
                    else:
                        print('no existe')
                        filename = fs.save(imagen.name, imagen)
                        uploaded_file_url = fs.url(filename)
                else:
                    if os.path.isfile(f'media/servAD/{servicio_edit[5]}'):
                        print('existe')
                        os.remove(f'media/servAD/{servicio_edit[5]}')
                        filename = fs.save(imagen.name, imagen)
                        uploaded_file_url = fs.url(filename)
                    else:
                        print('no existe')
                        filename = fs.save(imagen.name, imagen)
                        uploaded_file_url = fs.url(filename)
        except:
            nom = servicio_edit[5]
            pass
        nombre = nombre.strip()
        estado = estado.strip()
        precio = precio.strip()
        muestra = muestra.strip()
        descripcion = descripcion.strip()
        if nom != None:
            nom = nom
        else:
            nom = ''
        if len(nom) > 100:
            messages.error(
                request, f'Nombre de Imagen excede el Largo Máximo Permitido de 100 Caracteres, Modifique o elija otra para Continuar')
        else:
            if len(nombre) > 0 and len(precio) > 0 and len(muestra) > 0 and len(estado) > 0 and len(descripcion) > 0 and len(imagen) >= 0:
                with connection.cursor() as cursor:
                    try:
                        cursor.execute(
                            "SELECT COUNT(*)TT FROM SERVICIO_ADICIONAL WHERE NOMBRE LIKE %s and ID_SERVICIO != %s", [nombre, id])
                        validaExistencia = cursor.fetchone()
                        if validaExistencia[0] > 0:
                            messages.error(
                                request, f'El Nombre de Servicio {nombre} ya Existe')
                        else:
                            cursor.execute(f"""
                                                UPDATE SERVICIO_ADICIONAL SET NOMBRE = '{nombre}', DESCRIPCION = '{descripcion}', PRECIO = '{precio}',
                                                                            MOSTRAR_INICIO = '{muestra}', IMAGEN = '{nom}' , ESTADO = {estado} 
                                                                            WHERE ID_SERVICIO = '{id}'
                                                """)

                            messages.success(
                                request, f' {nombre} Modificado correctamente')
                            return redirect('servicios-list')
                    except Exception as e:
                        print(e)
                        pass
            else:
                messages.error(
                    request, f'Revise Campos Obligatorios. Completelos para Continuar')

    data = {
        'uploaded_file_url': uploaded_file_url,
        'servicio_edit': servicio_edit,
    }

    return render(request, 'Empleados/Servicios/Adicional/edit-servicio-ad.html', data)


def eliminar_servicioad(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "UPDATE SERVICIO_ADICIONAL SET ESTADO = %s WHERE ID_SERVICIO = %s", [0, id])
        except Exception as e:
            print(e)
            pass
    messages.success(request, "Eliminado correctamente")
    return redirect('servicios-list')


# ***Módulo:Empleados*** Opción: servicios productos
def nuevo_producto(request):
    proveedor = ''
    proveedor2 = ''
    tipo_prod = ''
    tipo_prod2 = ''
    cat_prod = ''
    cat_prod2 = ''
    nom_prod = ''
    precio = ''
    estado =''
    stock_actual = ''
    stock_critico = ''
    fecha_vence = ''
    tproductos = ''
    proveedores = ''
    categorias = ''
    fecha_vence2 = ''
    codigo = ''
    ttproductos = ''
    ttprodID = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT ID_TIPO_CLIENTE FROM TIPO_CLIENTE WHERE DESCRIPCION LIKE %s", ['Proveedor'])
            tipo_cliente_db = cursor.fetchone()
            cursor.execute("SELECT CODIGO, (RUT_EMPRESA||'-'|| DV), RAZON_SOCIAL FROM CLIENTE WHERE ID_TIPO_CLIENTE = %s AND ESTATUS = 1", [tipo_cliente_db[0]])
            proveedores = cursor.fetchall()
            cursor.execute("SELECT ID_TIPO_PRODUCTO, DESCRIPCION, ESTADO FROM TIPO_PRODUCTO WHERE ESTADO = 1")
            tproductos = cursor.fetchall()  
            cursor.execute("SELECT ID_CATEGORIA, DESCRIPCION, ESTATUS FROM CATEGORIA WHERE ESTATUS = 1")
            categorias = cursor.fetchall()
            cursor.execute("SELECT COUNT(*)AS TT FROM PRODUCTO")
            ttproductos =  cursor.fetchone()
            if ttproductos:
                ttprodID = ttproductos[0]+1
            else:
                ttprodID = 1
            ttprodID = str(ttprodID)
        except Exception as e:
            print(e)
            pass
    if request.method == "POST":
        proveedor = request.POST['proveedor']
        tipo_prod = request.POST['tipo_prod']
        cat_prod = request.POST['cat_prod']
        nom_prod = request.POST['nom_prod']
        precio = request.POST['precio']
        estado = request.POST['estado']
        stock_actual = request.POST['stock_actual']
        stock_critico = request.POST['stock_critico']
        fecha_vence = request.POST['fecha_vence']
        precio = precio.strip()
        nom_prod = nom_prod.strip()
        stock_actual = stock_actual.strip()
        stock_critico = stock_critico.strip()
        fecha_vence = fecha_vence.strip()

        if len(proveedor) > 0 and len(tipo_prod)>0 and len(cat_prod) > 0 and len(precio) > 0 and precio.isnumeric() and len(nom_prod) > 0 and len(stock_actual) > 0 and len(stock_critico) > 0 and len(fecha_vence) >= 0:
            if len(proveedor) == 1:
                proveedor2 = '00'+proveedor            
            elif len(proveedor) == 2:
                proveedor2 = '0'+proveedor                    
            else:
                proveedor2 = proveedor
            if len(tipo_prod) == 1:
                tipo_prod2 = '00'+tipo_prod            
            elif len(tipo_prod) == 2:
                tipo_prod2 = '0'+tipo_prod                    
            else:
                tipo_prod2 = tipo_prod
            if len(cat_prod) == 1:
                cat_prod2 = '00'+cat_prod            
            elif len(cat_prod) == 2:
                cat_prod2 = '0'+cat_prod                    
            else:
                cat_prod2 = cat_prod
            if len(fecha_vence):
                fecha_vence2 = fecha_vence.replace('-', '')
            else:
                fecha_vence2 = '00000000'                                        
            codigo = proveedor2+fecha_vence2+cat_prod2+tipo_prod2+ttprodID
            print(codigo)
            print(fecha_vence)
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        f"""
                        INSERT INTO PRODUCTO 
                            (ESPECIFICACION, DESCRIPCION, PRECIO, STOCK, STOCK_CRITICO, FECHA_VENCIMIENTO, ESTADO, ID_CATEGORIA, ID_TIPO_PRODUCTO)
                        VALUES ('{codigo}', '{nom_prod}','{precio}', '{stock_actual}', '{stock_critico}', '{fecha_vence}', '{estado}', '{cat_prod}', '{tipo_prod}')
                        """)
                    messages.success(request, f"Producto {nom_prod} Creado Correctamente con Código: {codigo}")
                    return redirect('productos-list')
                except Exception as e:
                    print(e)
                    pass
                    
        else:
            messages.error(
                request, f'Revise Campos Obligatorios. Completelos para Continuar')
    data = {
    'nom_prod':nom_prod,
    'precio': precio,
    'estado': estado,
    'stock_actual':stock_actual,
    'stock_critico':stock_critico,
    'fecha_vence':fecha_vence,    
    'proveedores':proveedores,
    'tproductos':tproductos,
    'categorias':categorias,
    'codigo':codigo
    }        

    return render(request, 'Empleados/Productos/producto.html', data)


def edit_producto(request,id):
    #Variables de Data del Producto
    data_producto =''
    proveedores = ''
    idProveedor = ''
    proveedor_sel = ''
    tipos_prod = ''
    tipo_prod_sel = ''
    cats_prod = ''
    cat_sel = ''
    fechaT = ''
    fecha = ''
    #Variables del POST
    nom_prod = ''
    precio = ''
    estado =''
    stock_actual = ''
    stock_critico = ''
    fecha_vence = ''
    proveedores = ''
    codigo = ''    
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"SELECT * FROM PRODUCTO WHERE ID_PRODUCTO = {id}")            
            data_producto = cursor.fetchone()
            if not data_producto:
                messages.error(
                    request, 'El de Producto que desea editar No Existe o fue eliminado')
                return redirect('productos-list')
            else:
                codigo = data_producto[1]
                #Extrae Proveedores
                cursor.execute("SELECT ID_TIPO_CLIENTE FROM TIPO_CLIENTE WHERE DESCRIPCION LIKE %s", ['Proveedor'])
                tipo_cliente_db = cursor.fetchone()
                cursor.execute(f"""SELECT ID_CLIENTE AS "0", (RUT_EMPRESA ||'-'|| DV) AS "1", RAZON_SOCIAL AS "2" FROM CLIENTE WHERE ESTATUS = 1 AND ID_TIPO_CLIENTE = {tipo_cliente_db[0]}""")
                proveedores = cursor.fetchall()
                #Extrae Proveedor
                idProveedor = data_producto[1] #Se guarda Codigo del Producto (Almacena Proveedor)
                idProveedor = idProveedor[0:3] #Se extrae Código que Pertecene al Proveedor
                #Se extrae proveedor Seleccionado
                cursor.execute(f"""SELECT ID_CLIENTE AS "0", (RUT_EMPRESA ||'-'|| DV) AS "1", RAZON_SOCIAL AS "2" 
                                FROM CLIENTE WHERE ID_TIPO_CLIENTE = {tipo_cliente_db[0]} AND CODIGO = {idProveedor}""")
                proveedor_sel = cursor.fetchone() # Se Guardan datos del Proveedor
                #Se extrae Tipos de Productos
                cursor.execute("SELECT * FROM TIPO_PRODUCTO WHERE ESTADO = 1")
                tipos_prod = cursor.fetchall()
                #Se extrae Tipo de Producto Seleccionado
                cursor.execute(f"SELECT * FROM TIPO_PRODUCTO WHERE ESTADO = 1 AND ID_TIPO_PRODUCTO = {data_producto[8]}")
                tipo_prod_sel = cursor.fetchone()                
                #Se extrae categorias 
                cursor.execute("SELECT * FROM CATEGORIA WHERE ESTATUS = 1")
                cats_prod = cursor.fetchall()           
                #Se extrae Categoria Seleccionada
                cursor.execute(f"SELECT * FROM CATEGORIA WHERE ESTATUS = 1 AND ID_CATEGORIA = {data_producto[7]}")
                cat_sel = cursor.fetchone()  
                formato = '%Y-%m-%d'
                fechaT = data_producto[6]
                if fechaT:
                    fecha = fechaT.strftime(formato)
                else:
                    fecha = ''                   
        except Exception as e:
            print(e)

    if request.method == "POST":
        
        nom_prod = request.POST['nom_prod']
        precio = request.POST['precio']
        estado = request.POST['estado']
        stock_actual = request.POST['stock_actual']
        stock_critico = request.POST['stock_critico']
        fecha_vence = request.POST['fecha_vence']
        precio = precio.strip()
        nom_prod = nom_prod.strip()
        stock_actual = stock_actual.strip()
        stock_critico = stock_critico.strip()
        fecha_vence = fecha_vence.strip()

        if  len(precio) > 0 and precio.isnumeric() and len(nom_prod) > 0 and len(stock_actual) > 0 and len(stock_critico) > 0 and len(fecha_vence) >= 0:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        f"""
                        UPDATE PRODUCTO SET DESCRIPCION =  '{nom_prod}', PRECIO = '{precio}', STOCK = '{stock_actual}',
                               STOCK_CRITICO = '{stock_critico}', FECHA_VENCIMIENTO = '{fecha_vence}', ESTADO = '{estado}'
                               WHERE ID_PRODUCTO = {id}
                        """)
                    messages.success(request, f"Producto {nom_prod} Modificado Correctamente con Código: {codigo}")
                    return redirect('productos-list')
                except Exception as e:
                    print(e)
                    pass
        else:
            messages.error(
                request, f'Revise Campos Obligatorios. Completelos para Continuar')
    print(data_producto)
    data = {
        'data_producto': data_producto,
        'proveedores':proveedores,
        'proveedor_sel':proveedor_sel,
        'tipos_prod':tipos_prod,
        'tipo_prod_sel':tipo_prod_sel,
        'cats_prod':cats_prod,
        'cat_sel': cat_sel,
        'fecha':fecha
    }    
    return render(request, 'Empleados/Productos/edit_producto.html', data)

def eliminar_producto(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "UPDATE PRODUCTO SET ESTADO = %s WHERE ID_PRODUCTO = %s", [0, id])
        except Exception as e:
            print(e)
            pass
    messages.success(request, "Producto Eliminado correctamente")
    return redirect('productos-list')


def productos(request):
    productos = ''
    i = 0
    now = ''
    now = datetime.now()
    now =now.strftime('%d-%m-%Y')
    mensaje = ''
    print(now)
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                """
                SELECT 
                    P.ID_PRODUCTO AS "0", P.ESPECIFICACION AS "1", C.DESCRIPCION AS "2", TP.DESCRIPCION AS "3", P.DESCRIPCION AS "4",
                    P.PRECIO AS "5", P.STOCK AS "6", P.STOCK_CRITICO AS "7", P.FECHA_VENCIMIENTO AS "8", P.ESTADO AS "9"
                FROM PRODUCTO P 
                JOIN CATEGORIA C ON P.ID_CATEGORIA = C.ID_CATEGORIA
                JOIN TIPO_PRODUCTO TP ON P.ID_TIPO_PRODUCTO = TP.ID_TIPO_PRODUCTO
                """
                )
            productos = cursor.fetchall()
            i = 0
            for prod in productos:
                print(prod[8])
                if prod[6] <= prod[7]:
                    mensaje = ( f"El Producto {prod[4].upper()} presenta un Stock Inferior o Igual al Crítico")
                    i= i + 1
                    if i > 1:
                        mensaje = ("Existe más de un Producto con Stock Inferior o Igual al Crítico")
        except Exception as e:
            print(e)
            messages.error(request, f"Error en consulta: {e}")
            pass
    data = {
        'productos':productos,
        'now':now,
        'mensaje':mensaje
     
    }
    return render(request, 'Empleados/Productos/productos.html', data)


def tipo_producto(request):
    nombre_tipo = ''
    estado = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute("""SELECT ID_TIPO_PRODUCTO, DESCRIPCION, ESTADO FROM TIPO_PRODUCTO """)
            tipo_productos = cursor.fetchall()
        except Exception as e:
            print(e)
            pass
    if request.method == "POST":
        nombre_tipo = request.POST['nombre']
        estado = request.POST['estado']
        if len(nombre_tipo) > 0 and len(estado) > 0:
            with connection.cursor() as cursor:
                try:
                    nombre_tipo = nombre_tipo.strip()
                    cursor.execute(
                        "SELECT COUNT(*)TT FROM TIPO_PRODUCTO WHERE DESCRIPCION LIKE %s", [nombre_tipo])
                    validaExistencia = cursor.fetchone()
                    if validaExistencia[0] > 0:
                        messages.error(
                            request, f'El Nombre de Tipo de Producto {nombre_tipo} ya Existe')
                    else:
                        cursor.execute(
                            f"""INSERT INTO TIPO_PRODUCTO (ESTADO, DESCRIPCION) VALUES ({estado}, '{nombre_tipo}')""")
                        messages.success(
                            request, f'Se ha registrado un Nuevo Tipo de Comedor con nombre {nombre_tipo}')
                        return redirect('tipo-producto')
                except Exception as e:
                    print(e)
                    messages.error(
                        request, f'Error al ejecutar consulta, Revisa Insert {e}')
                    pass
        else:
            messages.error(
                request, f'Campo Nombre y Estado Obligatorios. Completelos para Continuar')
    data = {
        'tipo_productos': tipo_productos,
        
    }

    return render(request, 'Empleados/Productos/tipo_producto.html', data)

def edit_tipo_producto(request, id):

    with connection.cursor() as cursor:
        try:
            cursor.execute(f"SELECT ID_TIPO_PRODUCTO, DESCRIPCION, ESTADO FROM TIPO_PRODUCTO WHERE ID_TIPO_PRODUCTO = {id}")
            tipo_producto = cursor.fetchone()
            if not tipo_producto:
                messages.error(
                    request, 'El Tipo de Producto que desea editar No Existe o fue eliminado')
                return redirect('tipo-producto')
        except Exception as e:
            print(e)

    if request.method == "POST":
        nombre_tipo = request.POST['nombre']
        estado = request.POST['estado']
        nombre_tipo = nombre_tipo.strip()
        if len(nombre_tipo) > 0 and len(estado) > 0:
            with connection.cursor() as cursor:
                try:
                    nombre_tipo = nombre_tipo.strip()
                    cursor.execute(
                        "SELECT COUNT(*)TT FROM TIPO_PRODUCTO WHERE DESCRIPCION LIKE %s and ID_TIPO_PRODUCTO != %s", [nombre_tipo, id])
                    validaExistencia = cursor.fetchone()
                    if validaExistencia[0] > 0:
                        messages.error(
                            request, f'El Nombre de Tipo de Producto {nombre_tipo} ya Existe')
                    else:
                        cursor.execute(
                            f"""UPDATE TIPO_PRODUCTO SET ESTADO = {estado}, DESCRIPCION='{nombre_tipo}' WHERE ID_TIPO_PRODUCTO = {id} """)
                        messages.success(
                            request, f'Se ha Modificado el Tipo de Producto con nombre {nombre_tipo} Correctamente')
                        return redirect('tipo-producto')
                except Exception as e:
                    print(e)
                    messages.error(
                        request, f'Error al ejecutar consulta, Revisa Insert {e}')
                    pass
        else:
            messages.error(
                request, f'Campo Nombre y Estado Obligatorios. Completelos para Continuar')
    data = {
        'tipo_producto': tipo_producto,
    }
    return render(request, 'Empleados/Productos/edit_tipo_prod.html', data)


def eliminar_tipo_producto(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "UPDATE TIPO_PRODUCTO SET ESTADO = %s WHERE ID_TIPO_PRODUCTO = %s", [0, id])
        except Exception as e:
            print(e)
            pass
    messages.success(request, "Eliminado correctamente")
    return redirect('tipo-producto')


def categoria(request):
    categoria = ''
    estado = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute("""SELECT ID_CATEGORIA, DESCRIPCION, ESTATUS FROM CATEGORIA """)
            categorias = cursor.fetchall()
        except Exception as e:
            print(e)
            pass
    if request.method == "POST":
        categoria = request.POST['nombre']
        estado = request.POST['estado']
        categoria = categoria.strip()
        if len(categoria) > 0 and len(estado) > 0:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        "SELECT COUNT(*)TT FROM CATEGORIA WHERE DESCRIPCION LIKE %s", [categoria])
                    validaExistencia = cursor.fetchone()
                    if validaExistencia[0] > 0:
                        messages.error(
                            request, f'La Categoria {categoria} ya Existe')
                    else:
                        cursor.execute(
                            f"""INSERT INTO CATEGORIA (ESTATUS, DESCRIPCION) VALUES ({estado}, '{categoria}')""")
                        messages.success(
                            request, f'Se ha registrado una Categoria con nombre {categoria} de Manera Correcta')
                        return redirect('categoria-new')
                except Exception as e:
                    print(e)
                    messages.error(
                        request, f'Error al ejecutar consulta, Revisa Insert {e}')
                    pass
        else:
            messages.error(
                request, f'Campo Nombre y Estado Obligatorios. Completelos para Continuar')
    data = {
        'categorias': categorias
    }
    return render(request, 'Empleados/Productos/categoria.html', data)


def edit_categoria(request, id):

    with connection.cursor() as cursor:
        try:
            cursor.execute(f"SELECT ID_CATEGORIA, DESCRIPCION, ESTATUS FROM CATEGORIA WHERE ID_CATEGORIA = {id}")
            categoria = cursor.fetchone()
            if not tipo_producto:
                messages.error(
                    request, 'La Categoria que desea editar No Existe o fue eliminado')
                return redirect('tipo-producto')
        except Exception as e:
            print(e)

    if request.method == "POST":
        nom_cat = request.POST['nombre']
        estado = request.POST['estado']
        nom_cat = nom_cat.strip()
        if len(nom_cat) > 0 and len(estado) > 0:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        "SELECT COUNT(*)TT FROM CATEGORIA WHERE DESCRIPCION LIKE %s and ID_CATEGORIA != %s", [nom_cat, id])
                    validaExistencia = cursor.fetchone()
                    if validaExistencia[0] > 0:
                        messages.error(
                            request, f'La Categoria {nom_cat} ya Existe')
                    else:
                        cursor.execute(
                            f"""UPDATE CATEGORIA SET ESTATUS = {estado}, DESCRIPCION='{nom_cat}' WHERE ID_CATEGORIA = {id} """)
                        messages.success(
                            request, f'Se ha Modificado La Categoria con nombre {nom_cat} Correctamente')
                        return redirect('categoria-new')
                except Exception as e:
                    print(e)
                    messages.error(
                        request, f'Error al ejecutar consulta, Revisa Insert {e}')
                    pass
        else:
            messages.error(
                request, f'Campo Nombre y Estado Obligatorios. Completelos para Continuar')
    data = {
        'categoria': categoria,
    }
    return render(request, 'Empleados/Productos/edit_categoria.html', data)


def eliminar_categoria(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "UPDATE CATEGORIA SET ESTATUS = %s WHERE ID_CATEGORIA = %s", [0, id])
        except Exception as e:
            print(e)
            pass
    messages.success(request, "Eliminado correctamente")
    return redirect('categoria-new')


# ***Módulo:Empleados*** Opción: ordenes pedidos

def nueva_ordenPedido(request):
    mensaje = ''
    idProveedor = ''
    inicio_index =  0
    productos = ''
    proveedor = ''
    fecha = ''
    observacion = None
    proveedores = None

    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT ID_TIPO_CLIENTE FROM TIPO_CLIENTE WHERE DESCRIPCION LIKE %s", ['Proveedor'])
            idProveedor = cursor.fetchone()
            idProveedor = idProveedor[0]
            cursor.execute(
                f"""SELECT CODIGO AS "0" ,(RUT_EMPRESA ||'-'|| DV) AS "1", RAZON_SOCIAL AS "2"
                FROM CLIENTE 
                WHERE ID_TIPO_CLIENTE = {idProveedor} AND ESTATUS = 1""")

            proveedores = cursor.fetchall()
        except Exception as e:
            print(e)
            pass
    
    if request.method == "POST":
        #
        # Post primer formulario
        #
        proveedor = request.POST['proveedor']
        fecha = request.POST['fecha']
        try:
            observacion = request.POST['observacion']
        except:
            pass
        if len(proveedor) <1 or len(fecha) <1:
            messages.warning(request, 'Campo Proveedor y Fecha Emisión son Obligatorios. Completos para Continuar.')
        else:
            if len(proveedor) ==1:
                codprovedor = '00'+proveedor
            elif len(proveedor) ==2:
                codprovedor = '0'+proveedor
            else:
                codprovedor = proveedor

            print(codprovedor)              
            with connection.cursor() as cursor:
                try:
                    cursor.execute(f"SELECT COUNT(*) AS TT FROM PRODUCTO WHERE substr(ESPECIFICACION, 1, 3) = '{codprovedor}'")
                    validaProdProveedor = cursor.fetchone()
                    validaProdProveedor = validaProdProveedor[0]
                    if validaProdProveedor >0:
                        mensaje = 'sigue'
                        print('Tiene Productos')
                        cursor.execute(f"""SELECT ID_PRODUCTO AS "0", ESPECIFICACION AS "1", DESCRIPCION  AS "2", STOCK AS "3", STOCK_CRITICO AS "4"
                          FROM PRODUCTO WHERE substr(ESPECIFICACION, 1, 3) = '{codprovedor}' """)
                        productos = cursor.fetchall()
                        
                        cantidades_list = request.POST.getlist('cant')
                        productos_list = request.POST.getlist('prd')
                        
                        indice = 0
                        productos_cant = {}

                        for cantidad in cantidades_list:
                            if int(cantidad) > 0:
                                productos_cant[int(productos_list[indice])] = int(cantidad)
                            else:
                                messages.error(request, 'La Cantidad Mínima permitida es 1')
                            indice = indice + 1
                        
                        #
                        # Validar que se ingresaron productos
                        #
                        if len(productos_cant) > 0:
                            #
                            # Crear Orden de pedido
                            #

                            #
                            # Obtener empleado
                            #
                            cursor.execute("SELECT ID_EMPLEADO FROM EMPLEADO " \
                                "WHERE ID_USUARIO = %s", [request.user.id])
                            empleado_db = cursor.fetchone()

                            #
                            # Obtener Estado Orden Pedido (Enviado)
                            #
                            cursor.execute("SELECT ID_ESTATUS_ORDEN_PEDIDO FROM ESTATUS_ORDEN_PEDIDO " \
                                "WHERE DESCRIPCION LIKE %s", ['ENVIADA'])
                            estatus_orden_pedido_db = cursor.fetchone()

                            #
                            # Obtener Cliente (Proveedor)
                            #
                            cursor.execute("SELECT ID_CLIENTE FROM CLIENTE " \
                                "WHERE CODIGO = %s", [proveedor])
                            cliente_db = cursor.fetchone()

                            #
                            # Insertar Orden de pedido
                            #
                            if observacion == '':
                                cursor.execute("INSERT INTO ORDEN_PEDIDO (FECHA_EMISION, ID_ESTATUS_ORDEN_PEDIDO, ID_CLIENTE, ID_EMPLEADO) " \
                                    "VALUES (%s, %s, %s, %s)", [fecha, estatus_orden_pedido_db[0], cliente_db[0], empleado_db[0]])
                            else:
                                cursor.execute("INSERT INTO ORDEN_PEDIDO (FECHA_EMISION, ID_ESTATUS_ORDEN_PEDIDO, ID_CLIENTE, ID_EMPLEADO, OBSERVACION) " \
                                    "VALUES (%s, %s, %s, %s, %s)", [fecha, estatus_orden_pedido_db[0], cliente_db[0], empleado_db[0], observacion])
                            
                            #
                            # Obtener ultima Orden de pedido
                            #
                            cursor.execute("SELECT ID_ORDEN_PEDIDO FROM ORDEN_PEDIDO ORDER BY ID_ORDEN_PEDIDO DESC")
                            orden_pedido_db = cursor.fetchone()

                            #
                            # Insertar Detalles Orden de Pedido
                            #
                            for producto_k, cantidad_v in productos_cant.items():
                                producto_id = producto_k
                                cantidad  = cantidad_v

                                cursor.execute("INSERT INTO DETALLE_ORDEN_PEDIDO (CANTIDAD, ID_ORDEN_PEDIDO, ID_PRODUCTO) " \
                                    "VALUES (%s, %s, %s)", [cantidad, orden_pedido_db[0], producto_id])
                            
                            messages.success(request, f'Orden de pedido #{orden_pedido_db[0]} creada correctamente!')
                            return redirect('ordenes-pedidos-list')
                    else:
                        messages.error(request, 'Lo sentimos. No se encontraron Productos Asociados al Proveedor. Cree Productos o Elija otro Proveedor para Continuar.')
                    
                except Exception as e:
                    print(e)
                    pass        
    data = {
        'proveedores':proveedores,
        'mensaje': mensaje,
        'inicio_index': inicio_index,
        'productos':productos,
        'observacion': observacion,
        'proveedor': proveedor,
        'fecha': fecha
    }

    return render(request, 'Empleados/OrdenesPedidos/orden_pedido.html', data)


def ordenes_pedido(request):
    ordenes_pedido_db = None

    with connection.cursor() as cursor:
        try:
            if not request.user.is_proveedor:
                cursor.execute("""SELECT OP.ID_ORDEN_PEDIDO, CL.RAZON_SOCIAL, TO_CHAR(OP.FECHA_EMISION,'DD-MM-YYYY'), ROP.FECHA_ENTREGA,
                    SUM(DOP.CANTIDAD), EOP.DESCRIPCION, ROP.OBSERVACION
                    FROM ORDEN_PEDIDO OP
                    JOIN DETALLE_ORDEN_PEDIDO DOP ON OP.ID_ORDEN_PEDIDO = DOP.ID_ORDEN_PEDIDO
                    JOIN ESTATUS_ORDEN_PEDIDO EOP ON OP.ID_ESTATUS_ORDEN_PEDIDO = EOP.ID_ESTATUS_ORDEN_PEDIDO 
                    LEFT JOIN RECEPCION_ORDEN_PEDIDO ROP ON OP.ID_ORDEN_PEDIDO = ROP.ID_ORDEN_PEDIDO 
                    JOIN CLIENTE CL ON OP.ID_CLIENTE = CL.ID_CLIENTE
                    GROUP BY OP.ID_ORDEN_PEDIDO, CL.RAZON_SOCIAL, OP.FECHA_EMISION, ROP.FECHA_ENTREGA, 
                    EOP.DESCRIPCION, ROP.OBSERVACION""")

                ordenes_pedido_db = cursor.fetchall()
                print(ordenes_pedido_db)
            else:
                pass
            
        except Exception as e:
            print(e)
            pass
    
    data = {
        "pedidos": ordenes_pedido_db
    }

    return render(request, 'Empleados/OrdenesPedidos/ordenes_pedido.html', data)


def edit_ordenPedido(request, id):
    orden_pedido_db = None
    detalle_orden_pedido_db = None
    obs = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT ID_ESTATUS_ORDEN_PEDIDO FROM ESTATUS_ORDEN_PEDIDO " \
                "WHERE DESCRIPCION LIKE %s", ['ENVIADA'])
            estatus_db = cursor.fetchone()[0]
            print(estatus_db)
            cursor.execute(f"""SELECT OP.ID_ORDEN_PEDIDO AS "0", EOP.DESCRIPCION AS "1", ( EM.NOMBRES || ' ' || EM.APELLIDO_P || ' ' || EM.APELLIDO_M) AS "2", 
                OP.FECHA_EMISION AS "3", (CL.RUT_EMPRESA || '-' || CL.DV) AS "4", CL.RAZON_SOCIAL AS "5", OP.OBSERVACION AS "6" 
                FROM ORDEN_PEDIDO OP 
                JOIN ESTATUS_ORDEN_PEDIDO EOP ON OP.ID_ESTATUS_ORDEN_PEDIDO = EOP.ID_ESTATUS_ORDEN_PEDIDO 
                JOIN CLIENTE CL ON OP.ID_CLIENTE = CL.ID_CLIENTE 
                JOIN EMPLEADO EM ON OP.ID_EMPLEADO = EM.ID_EMPLEADO 
                WHERE OP.ID_ORDEN_PEDIDO = {id} and OP.ID_ESTATUS_ORDEN_PEDIDO = {estatus_db}""")
            orden_pedido_db = cursor.fetchone()
            if orden_pedido_db is None:
                messages.error(request, 'Error, el número de Orden de Pedido No existe o o su estado no es ENVIADA')
                return redirect('ordenes-pedidos-list')
            if orden_pedido_db[6] == None:
                obs == ''
            else:
                obs == orden_pedido_db[6]
            cursor.execute(f"""SELECT PR.ESPECIFICACION AS "0", PR.DESCRIPCION AS "1", PR.STOCK AS "2", 
                PR.STOCK_CRITICO AS "3", DOP.CANTIDAD AS "4", DOP.ID_PRODUCTO AS "5" 
                FROM PRODUCTO PR 
                JOIN DETALLE_ORDEN_PEDIDO DOP ON DOP.ID_PRODUCTO = PR.ID_PRODUCTO 
                WHERE DOP.ID_ORDEN_PEDIDO = {id}""")
            detalle_orden_pedido_db = cursor.fetchall()
            
        except Exception as e:
            print(e)
            pass
    
        if request.method == 'POST':
            fecha_emision = request.POST['fec-emision']
            observacion = request.POST['observacion']
            cantidades = request.POST.getlist('cantidad')
            detalle_orden = request.POST.getlist('detall-id')

            print(request.POST)

            print(fecha_emision)
            print(observacion)
            print('cantidades',cantidades)
            print('detalle-id',detalle_orden)

            indice = 0
            if "0" in cantidades:
                messages.error(request, 'La Cantidad Mínima permitida es 1')
            else:
                for cantidad in cantidades:
                    cursor.execute("UPDATE DETALLE_ORDEN_PEDIDO SET CANTIDAD = %s " \
                    "WHERE ID_PRODUCTO = %s AND ID_ORDEN_PEDIDO = %s", [cantidad, detalle_orden[indice], id])

                    indice = indice + 1
                
                cursor.execute("UPDATE ORDEN_PEDIDO SET FECHA_EMISION = %s, OBSERVACION = %s " \
                    "WHERE ID_ORDEN_PEDIDO = %s", [fecha_emision, observacion, id])

                messages.success(request, 'Orden de pedido modificada correctamente')
                return redirect('ordenes-pedidos-list')
    
    data = {
        'orden_pedido': orden_pedido_db,
        'detalle_pedido': detalle_orden_pedido_db,
        'obs':obs
    }

    return render(request, 'Empleados/OrdenesPedidos/edit_orden_pedido.html', data)

def check_ordenPedido(request, id):
    orden_pedido_db = None
    detalle_orden_pedido_db = None
    n_detalles = None

    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT ID_ESTATUS_ORDEN_PEDIDO FROM ESTATUS_ORDEN_PEDIDO " \
                "WHERE DESCRIPCION LIKE %s", ['PENDIENTE RECEPCION'])
            estatus_db = cursor.fetchone()[0]            
            cursor.execute(f"""SELECT OP.ID_ORDEN_PEDIDO AS "0", EOP.DESCRIPCION AS "1", ( EM.NOMBRES || ' ' || EM.APELLIDO_P || ' ' || EM.APELLIDO_M) AS "2", 
                OP.FECHA_EMISION AS "3", (CL.RUT_EMPRESA || '-' || CL.DV) AS "4", CL.RAZON_SOCIAL AS "5", OP.OBSERVACION AS "6" 
                FROM ORDEN_PEDIDO OP 
                JOIN ESTATUS_ORDEN_PEDIDO EOP ON OP.ID_ESTATUS_ORDEN_PEDIDO = EOP.ID_ESTATUS_ORDEN_PEDIDO 
                JOIN CLIENTE CL ON OP.ID_CLIENTE = CL.ID_CLIENTE 
                JOIN EMPLEADO EM ON OP.ID_EMPLEADO = EM.ID_EMPLEADO 
                WHERE OP.ID_ORDEN_PEDIDO = {id} and OP.ID_ESTATUS_ORDEN_PEDIDO = {estatus_db}""")
            orden_pedido_db = cursor.fetchone()
            if orden_pedido_db is None:
                messages.error(request, 'Error, el número de Orden de Pedido No existe o su estado no es PENDIENTE RECEPCIÓN')
                return redirect('ordenes-pedidos-list')
            cursor.execute(f"""SELECT PR.ESPECIFICACION AS "0", PR.DESCRIPCION AS "1", DOP.CANTIDAD AS "2", DOP.ID_ORDEN_PEDIDO AS "3" 
                FROM PRODUCTO PR 
                JOIN DETALLE_ORDEN_PEDIDO DOP ON DOP.ID_PRODUCTO = PR.ID_PRODUCTO 
                WHERE DOP.ID_ORDEN_PEDIDO = {id}""")
            detalle_orden_pedido_db = cursor.fetchall()

            n_detalles = len(detalle_orden_pedido_db)
            
            if request.method == 'POST':
                observacion = request.POST["observacion"]

                #
                # Insertar INSERT a Recepcion Orden de Pedido y ejecutar Trigger
                #
                with connection.cursor() as cursor:
                    try:
                        cursor.execute("SELECT ID_ESTATUS_RECEP FROM ESTATUS_RECEPCION " \
                            "WHERE DESCRIPCION LIKE %s", ['Recepcionada'])
                        estatus_db = cursor.fetchone()
                        print(estatus_db)

                        now = datetime.now()
                        print(now)

                        if observacion is not None and observacion != '':
                            cursor.execute("INSERT INTO RECEPCION_ORDEN_PEDIDO (FECHA_ENTREGA, ID_ORDEN_PEDIDO, ID_ESTATUS_RECEP, OBSERVACION) " \
                                "VALUES (%s, %s, %s, %s)", [now, id, estatus_db[0], observacion])
                        else:
                            cursor.execute("INSERT INTO RECEPCION_ORDEN_PEDIDO (FECHA_ENTREGA, ID_ORDEN_PEDIDO, ID_ESTATUS_RECEP) " \
                                "VALUES (%s, %s, %s)", [now, id, estatus_db[0]])

                        messages.success(request, f'Orden de pedido #{id} recepcionada correctamente')
                        return redirect('ordenes-pedidos-list')
                    except Exception as e:
                        messages.error(request, 'Orden de pedido no se pudo modificar')
                        print(e)

                return redirect('ordenes-pedidos-list')
        except Exception as e:
            print(e)
            pass
    
    data = {
        'orden_pedido': orden_pedido_db,
        'detalle_pedido': detalle_orden_pedido_db,
        'n_detalles': n_detalles
    }

    return render(request, 'Empleados/OrdenesPedidos/check_rec_pedidos.html', data)

def anular_ordenPedido(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT ID_ESTATUS_ORDEN_PEDIDO FROM ESTATUS_ORDEN_PEDIDO " \
                "WHERE DESCRIPCION LIKE %s", ['ANULADA'])
            estatus_db = cursor.fetchone()

            cursor.execute("UPDATE ORDEN_PEDIDO SET ID_ESTATUS_ORDEN_PEDIDO = %s " \
                "WHERE ID_ORDEN_PEDIDO = %s", [estatus_db[0], id])

            messages.success(request, 'Orden de pedido modificada correctamente')
            return redirect('ordenes-pedidos-list')
        except Exception as e:
            messages.error(request, 'Orden de pedido no se pudo modificar')
            print(e)

    return redirect('ordenes-pedidos-list')

def rechazar_ordenPedido(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT ID_ESTATUS_ORDEN_PEDIDO FROM ESTATUS_ORDEN_PEDIDO " \
                "WHERE DESCRIPCION LIKE %s", ['RECHAZADO'])
            estatus_db = cursor.fetchone()

            cursor.execute("UPDATE ORDEN_PEDIDO SET ID_ESTATUS_ORDEN_PEDIDO = %s " \
                "WHERE ID_ORDEN_PEDIDO = %s", [estatus_db[0], id])

            messages.success(request, f'Orden de pedido #{id} rechazada correctamente')
            return redirect('ordenes-pedidos-list')
        except Exception as e:
            messages.error(request, 'Orden de pedido no se pudo modificar')
            print(e)

    return redirect('ordenes-pedidos-list')

#CAMBIAR FORMATO DE FECHA AL PASAR A PRODUCTIVO (ORACLE)
def documentos(request):
    docs = ''
    
    with connection.cursor() as cursor:
        try:
            
            cursor.execute("""
                SELECT D.ID_DOCUMENTO AS "0", TD.ABREVIADO AS "1",NVL(OC.ID_ORDEN_DE_COMPRA,0) AS "2",
                (CL.RUT_EMPRESA ||'-'|| CL.DV) AS "3",
                CL.RAZON_SOCIAL AS "4",D.FECHA_EMISION AS "5", D.MONTO_TOTAL AS "6" , ED.ID_ESTATUS_DOCUMENTO AS "7",
                ED.DESCRIPCION AS "8", NVL(OP.ID_ORDEN_PEDIDO,0) AS "9"
                FROM DOCUMENTO D
                JOIN TIPO_DOCUMENTO TD ON D.CODIGO_SII = TD.CODIGO_SII
                LEFT JOIN ORDEN_COMPRA OC ON D.ID_ORDEN_DE_COMPRA = OC.ID_ORDEN_DE_COMPRA
                LEFT JOIN ORDEN_PEDIDO OP ON D.ID_ORDEN_PEDIDO = OP.ID_ORDEN_PEDIDO
                JOIN CLIENTE CL ON OC.ID_CLIENTE = CL.ID_CLIENTE
                JOIN ESTATUS_DOCUMENTO ED ON D.ID_ESTATUS_DOCUMENTO = ED.ID_ESTATUS_DOCUMENTO
                          """)
            docs = cursor.fetchall()

        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            pass

    data = {
        'docs': docs,
     
    }

    return render(request, 'Empleados/Ventas/ventas.html',data)

def facturarOC(request, id):
    fechaEmision = ''
    with connection.cursor() as cursor:
        try:
            fechaEmision = datetime.now()
            print(fechaEmision)
            cursor.execute(f"""
                            SELECT ID_ORDEN_DE_COMPRA AS "0", 
                            MONTO_NETO AS "1", IVA AS "2", MONTO_TOTAL AS "3" 
                            FROM ORDEN_COMPRA WHERE ID_ORDEN_DE_COMPRA = {id}""")
            oc = cursor.fetchone()
            nroOC = oc[0]
            montoNeto = oc[1]
            iva = oc[2]
            montoTotal = oc[3]
            if not oc:
                messages.error(request, 'No se encontró detalle de la Orden de Compra')
            else:
                if montoNeto == None or iva == None or montoTotal == None:
                    messages.error(request, 'Lo sentimos, la orden de Compra No se puede facturar ya que no posee valores')
                else:
                    cursor.execute(f"""
                                    INSERT INTO DOCUMENTO (FECHA_EMISION, MONTO_NETO, IVA, MONTO_TOTAL, ID_ESTATUS_DOCUMENTO, ID_ORDEN_DE_COMPRA, CODIGO_SII)
                                    VALUES ('{fechaEmision}', '{montoNeto}', '{iva}', '{montoTotal}','1' , '{nroOC}', '33' )
                                    """) 
                    cursor.execute(f"SELECT ID_DOCUMENTO FROM DOCUMENTO WHERE ID_ORDEN_DE_COMPRA = {id}")
                    nroFactura = cursor.fetchone()
                    nroFactura = nroFactura[0]                   
                    cursor.execute(f"UPDATE ORDEN_COMPRA SET ID_ESTATUS_ORDEN_COMPRA = 2 WHERE ID_ORDEN_DE_COMPRA = {id}")
                    messages.success(request, f"Orden de Compra Facturada Correctamente con N° de Factura #{nroFactura}")

        except Exception as e:
            print(e)
            pass
    
    return redirect('oc-list-views') 

#Anular Factura
def notaCredito(request, id):
    fechaEmision = ''
    with connection.cursor() as cursor:
        try:
            fechaEmision = datetime.now()
            print(fechaEmision)
            cursor.execute(f"""
                    select ID_DOCUMENTO AS "0", monto_neto AS "1", iva AS "2", monto_total AS "3",
                    NVL(ID_ORDEN_DE_COMPRA,0) AS "4", NVL(ID_ORDEN_PEDIDO,0) AS "5"
                    from DOCUMENTO
                    where ID_DOCUMENTO = {id}
            """)
            fac = cursor.fetchone()
            nroFac = fac[0]
            montoNeto = fac[1]
            iva = fac[2]
            montoTotal = fac[3]
            nroOC = fac[4]
            nroOP = fac[5]
            if not fac:
                messages.error(request, 'No se encontró detalle de la Factura')
            else:
                if montoNeto == None or iva == None or montoTotal == None:
                    messages.error(request, 'Lo sentimos, la Factura No se Puede Anular ya que no posee valores')
                else:
                    if int(nroOC) > 0:
                        
                        #GENERA NOTA DE CRÉDITO PARA ORDEN DE COMPRA
                        print('generando NC')
                        cursor.execute(f"""
                                    INSERT INTO DOCUMENTO (FECHA_EMISION, MONTO_NETO, IVA, MONTO_TOTAL, ID_ESTATUS_DOCUMENTO, ID_ORDEN_DE_COMPRA, CODIGO_SII, doc_anulado)
                                    VALUES ('{fechaEmision}', '{montoNeto}', '{iva}', '{montoTotal}','1' , '{nroOC}', '61', '{id}' )
                                    """)                                         
                        cursor.execute(f"SELECT ID_DOCUMENTO FROM DOCUMENTO WHERE doc_anulado = {id}")
                        nroNotaCredito = cursor.fetchone()
                        nroNotaCredito = nroNotaCredito[0]
                        cursor.execute(f"UPDATE DOCUMENTO SET ID_ESTATUS_DOCUMENTO = 2 , fecha_anulacion = '{fechaEmision}' WHERE ID_DOCUMENTO = {id}")
                        messages.success(request, f"Nota de Crédito Generada Correctamente. N° de Nota de Crédito #{nroNotaCredito}")
                        #ACTUALIZA FACTURA                       
                    elif int(nroOP) > 0:
                        #GENERA NOTA DE CRÉDITO PARA ORDEN DE PEDIDO
                        cursor.execute(f"""
                                        INSERT INTO DOCUMENTO (fecha_emision, monto_neto, iva, monto_total, ID_ESTATUS_DOCUMENTO, ID_ORDEN_PEDIDO, CODIGO_SII, doc_anulado)
                                        VALUES ('{fechaEmision}', '{montoNeto}', '{iva}', '{montoTotal}','1' , '{nroOP}', '61', '{id}' )
                                        """) 
                        cursor.execute(f"SELECT ID_DOCUMENTO FROM DOCUMENTO WHERE doc_anulado = {id}")
                        nroNotaCredito = cursor.fetchone()
                        nroNotaCredito = nroNotaCredito[0]
                        messages.success(request, f"Nota de Crédito Generada Correctamente. N° de Nota de Crédito #{nroNotaCredito}")
                        #ACTUALIZA FACTURA
                        cursor.execute(f"UPDATE DOCUMENTO SET ID_ESTATUS_DOCUMENTO = 2 , fecha_anulacion = '{fechaEmision}' WHERE ID_DOCUMENTO = {id}")
                    else:
                        messages.error(request, 'Lo sentimos. Ocurrió un Problema al Generar Nota de Crédito (No se encontró Doc. Ref!)') 

        except Exception as e:
            print(e)
            messages.error(request, f'Lo sentimos. Ocurrió un Problema en: {e}') 
            pass
    
    return redirect('ventas') 

    
def orden_compra_views(request):
    ordenes_compras = ''
    ids = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                                SELECT DISTINCT OC.ID_ORDEN_DE_COMPRA AS "0", (CL.RUT_EMPRESA ||'-'|| CL.DV ) AS "1", CL.RAZON_SOCIAL AS "2",
                                        OC.CANT_HUESPED AS "3", OC.MONTO_TOTAL AS "4", upper(DOC.DESCRIPCION) AS "5", 
                                                OC.ID_ESTATUS_ORDEN_COMPRA as "6", DTC.INICIO_ESTADIA AS "7" , DTC.FINAL_ESTADIA AS "8", DTC.ID_DETALLE_ORDEN_DE_COMPRA  AS "9"
                                FROM ORDEN_COMPRA OC 
                                JOIN DETALLE_ORDEN_COMPRA DTC ON OC.ID_ORDEN_DE_COMPRA = DTC.ID_ORDEN_DE_COMPRA
                                JOIN CLIENTE CL ON OC.ID_CLIENTE = CL.ID_CLIENTE
                                JOIN ESTATUS_ORDEN_COMPRA DOC ON OC.ID_ESTATUS_ORDEN_COMPRA = DOC.ID_ESTATUS_ORDEN_COMPRA 
                          """)
            ordenes_compras = cursor.fetchall()
            if ordenes_compras[4] != '':
                ordenes_compras[4]
            else:
                ordenes_compras[4] = ''
        except Exception as e:
            print(e)
            pass

    data = {
        'ordenes_compras': ordenes_compras,
     
    }

    return render(request, 'Empleados/Ventas/oc-views.html', data)

def reservas(request):
    fdesde = ''
    fhasta = ''
    reservas = ''
    if request.method == "POST":
        fdesde = request.POST['fdesde']
        fhasta = request.POST['fhasta']
        if len(fdesde) <1  or len(fhasta) < 1:
            messages.warning(request, 'Los Campos de Fechas Son Obligatorios. Completelos para Continuar')
        else:
            if fdesde > fhasta:
                messages.error(request, 'La Fecha Desde No puede ser Mayor a la Fecha Hasta')

            else:
                with connection.cursor() as cursor:
                    try:
                        fdesde_obj = datetime.strptime(fdesde,'%Y-%m-%d' ) 
                        fhasta_obj = datetime.strptime(fhasta,'%Y-%m-%d' ) 

                        cursor.execute(f"""
                            SELECT R.ID_RESERVA AS "0", DOC.id_orden_de_compra AS "1", CL.razon_social AS "2", (H.rut ||'-'|| H.dv) AS "3 RUT",
                            (H.nombre ||' '|| H.apellido_p) AS "4 NOMBRE",TC.descripcion AS "5",HA.numero_habitacion AS "6",
                            THA.descripcion AS "7",  DOC.inicio_estadia AS "8 INI. ESTADIA", DOC.final_estadia AS "9 FIN. ESTADIA", 
                            R.check_in AS "10"
                            FROM RESERVA R
                            JOIN DETALLE_ORDEN_COMPRA DOC ON R.ID_DETALLE_ORDEN_DE_COMPRA = DOC.ID_DETALLE_ORDEN_DE_COMPRA
                            JOIN ORDEN_COMPRA OC ON DOC.ID_ORDEN_DE_COMPRA = OC.ID_ORDEN_DE_COMPRA
                            JOIN HUESPED H ON R.ID_HUESPED = H.ID_HUESPED
                            JOIN CLIENTE CL ON OC.ID_CLIENTE = CL.ID_CLIENTE
                            JOIN TIPO_COMEDOR TC ON R.ID_TIPO_COMEDOR = TC.ID_TIPO_COMEDOR
                            JOIN HABITACION HA ON R.ID_HABITACION = HA.ID_HABITACION
                            JOIN TIPO_HABITACION THA ON HA.ID_TIPO_HABITACION = THA.ID_TIPO_HABITACION
                            LEFT JOIN PLATO_SEMANAL P ON R.PLATO = P.ID_COMEDOR
                            WHERE DOC.inicio_estadia >= '{fdesde_obj}' AND  DOC.final_estadia <='{fhasta_obj}'
                        """)
                        reservas = cursor.fetchall()
                        if not reservas:
                            messages.error(request, 'No existen Resultados para las Fechas Indicadas')
                    except Exception as e:                        
                        print(e)
                        pass         
    data = {
        'reservas':reservas,
        'fdesde':fdesde,
        'fhasta':fhasta
    }       

    return render(request, 'Empleados/Ventas/reservas.html', data)

def check_in(request,id):
    huesped = ''
    platos = ''
    inicio_index =  0
    fdesde = ''
    fhasta = ''
    with connection.cursor() as cursor:     
        try:
            cursor.execute(f"""
                SELECT R.ID_RESERVA AS "0", (H.rut ||'-'|| H.dv) AS "1_RUT",
                (H.nombre ||' '|| H.apellido_p) AS "2 NOMBRE", HA.numero_habitacion AS "3",
                THA.descripcion AS "4",TC.descripcion AS "5",  DOC.inicio_estadia AS "6 INI. ESTADIA", 
                DOC.final_estadia AS "7 FIN. ESTADIA", R.check_in AS "8"
                FROM RESERVA R
                JOIN DETALLE_ORDEN_COMPRA DOC ON R.ID_DETALLE_ORDEN_DE_COMPRA = DOC.ID_DETALLE_ORDEN_DE_COMPRA
                JOIN ORDEN_COMPRA OC ON DOC.ID_ORDEN_DE_COMPRA = OC.ID_ORDEN_DE_COMPRA
                JOIN HUESPED H ON R.ID_HUESPED = H.ID_HUESPED
                JOIN CLIENTE CL ON OC.ID_CLIENTE = CL.ID_CLIENTE
                JOIN TIPO_COMEDOR TC ON R.ID_TIPO_COMEDOR = TC.ID_TIPO_COMEDOR
                JOIN HABITACION HA ON R.ID_HABITACION = HA.ID_HABITACION
                JOIN TIPO_HABITACION THA ON HA.ID_TIPO_HABITACION = THA.ID_TIPO_HABITACION
                WHERE R.ID_RESERVA = {id}
            """)
            huesped = cursor.fetchone()
            print(huesped)
            if not huesped:
                messages.error(request, 'Lo sentimos, La Reserva Buscada No existe o Fue Eliminada.')
                return redirect('reservas')
            else:
                print( huesped[8])
                if huesped[8] == 1:
                    messages.error(request, 'Lo sentimos, La Reserva ya está Finalizada.')
                    return redirect('reservas')
                else:
                    fdesde = huesped[6]
                    fhasta = huesped[7]
                    descripcion = huesped[5]
                    cursor.execute (f"""
                    SELECT P.ID_COMEDOR, P.DESCRIPCION, P.DIA_DESDE, P.DIA_HASTA, TC.DESCRIPCION
                    FROM PLATO_SEMANAL P
                    JOIN TIPO_COMEDOR TC ON P.ID_TIPO_COMEDOR = TC.ID_TIPO_COMEDOR
                    WHERE TC.DESCRIPCION LIKE '{descripcion}' AND  '{fdesde}' BETWEEN DIA_DESDE AND DIA_HASTA OR '{fhasta}' BETWEEN DIA_DESDE AND DIA_HASTA
                    """)     
                    platos = cursor.fetchall()
                    if not platos:
                        messages.error(request, 'Lo sentimos, No existen Platos Disponibles para ofrecer. Modifique o Agregue e Intente de Nuevo')
                        return redirect('reservas')
        except Exception as e:                        
            print(e)
            messages.error(request, 'Lo sentimos, La Reserva Buscada No existe o Fue Eliminada.')
            return redirect('reservas')
        print(huesped)

    if request.method == "POST":
        platoId = request.POST['plato']
        if not platoId:
            messages.warning(request, 'Seleccione un Plato para Continuar')
        else:
            with connection.cursor() as cursor:     
                try:            
                    cursor.execute(f"SELECT descripcion FROM PLATO_SEMANAL WHERE id_comedor = {platoId}")
                    platoDes = cursor.fetchone()
                    platoDes = platoDes[0]
                    cursor.execute(f"UPDATE RESERVA SET CHECK_IN = 1, PLATO = {platoId} WHERE ID_RESERVA ={id}")
                    messages.success(request, f'Check-In Realizado Correctamente. Plato Seleccionado para el Huésped: {platoDes}')
                    return redirect('reservas')
                except Exception as e:                        
                    print(e)
    data = {
        'huesped':huesped,
        'inicio_index': inicio_index,
        'platos':platos
        
    }  

    return render(request, 'Empleados/Ventas/check-in.html', data)



def print_pedidos(request, id):
    datos_empresa = ''
    orden_pedido_db = ''
    detatalles_op = ''
    total_op = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"""SELECT OP.ID_ORDEN_PEDIDO AS "0", UPPER(EOP.DESCRIPCION) AS "1", 
               UPPER( ( EM.NOMBRES || ' ' || EM.APELLIDO_P || ' ' || EM.APELLIDO_M)) AS "2", 
                (EM.RUT_EMPLEADO) AS "3", EM.DV AS "4",
                TO_CHAR(OP.FECHA_EMISION, 'DD-MM-YYYY') AS "5", (CL.RUT_EMPRESA) AS "6", CL.DV AS "7", 
                UPPER(CL.RAZON_SOCIAL) AS "8", OP.OBSERVACION AS "9" 
                FROM ORDEN_PEDIDO OP 
                JOIN ESTATUS_ORDEN_PEDIDO EOP ON OP.ID_ESTATUS_ORDEN_PEDIDO = EOP.ID_ESTATUS_ORDEN_PEDIDO 
                JOIN CLIENTE CL ON OP.ID_CLIENTE = CL.ID_CLIENTE 
                JOIN EMPLEADO EM ON OP.ID_EMPLEADO = EM.ID_EMPLEADO 
                WHERE OP.ID_ORDEN_PEDIDO = {id}""")
            orden_pedido_db = cursor.fetchone()
            if orden_pedido_db is None:
                messages.error(request, 'Error, el número de Orden de Pedido No existe o Fue Eliminada')
                return redirect('ordenes-pedidos-list')   
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
                
                cursor.execute(f"""
                SELECT P.ESPECIFICACION,  P.DESCRIPCION,DOP.CANTIDAD
                FROM DETALLE_ORDEN_PEDIDO DOP
                JOIN PRODUCTO P ON DOP.ID_PRODUCTO = P.ID_PRODUCTO
                WHERE ID_ORDEN_PEDIDO = {id}
                """)
                detatalles_op = cursor.fetchall()

                cursor.execute(f"""
                SELECT SUM(CANTIDAD) FROM DETALLE_ORDEN_PEDIDO WHERE ID_ORDEN_PEDIDO ={id} GROUP BY ID_ORDEN_PEDIDO
                """)
                total_op = cursor.fetchone()[0]
        except Exception as e:
            print(e)
            pass

    data = {
        'datos_empresa': datos_empresa,
        'orden_pedido_db':orden_pedido_db,
        'detatalles_op':detatalles_op,
        'total_op':total_op
    }
    return render(request, 'Empleados/OrdenesPedidos/print_pedidos.html', data)
def comentarios(request):
    return render(request, 'Empleados/comentarios.html')

def informes(request):

    informe = ''
    fecha_d = ''
    fecha_h = ''
    if request.method == 'POST':
        informe = request.POST['informe']
        try:
            fecha_d = request.POST['fecha_d']
            fecha_h = request.POST['fecha_h']
        except:    
            pass
        if informe == '':
            messages.warning(request, 'Debe Seleccionar un Informe para Continuar')
        else:
            if informe == 'op1':
               return redirect('informe-print',informe) 
            if informe == 'op2' and len(fecha_d)< 1 or len(fecha_h)<1:
                messages.warning(request, 'Debe Seleccionar las Fechas para Continuar')
            else:                     
                return redirect('informe-print',informe,fecha_d,fecha_h)                  
            
            if informe == 'op3' and len(fecha_d)< 1 or len(fecha_h)<1:    
                messages.warning(request, 'Debe Seleccionar las Fechas para Continuar')
            else:
                return redirect('informe-print',informe,fecha_d,fecha_h) 
              
            
    data = {
        'informe':informe
    }
    return render(request, 'Empleados/Informes/informe.html', data)

def informe_print(request, op, fd=None, fh=None):
    usuarios = ''
    usuarios_tt = 0
    resultado = ''
    formato = ''
    fechaD = ''
    fechaH = ''
    ordenes_compras = ''
    doc_tt = ''
    facturas = 0
    notacreditos = 0
    totalIng = 0
    with connection.cursor() as cursor:
            try:    
                if op == "op1":
                    cursor.execute("""
                    SELECT ROW_NUMBER() OVER (ORDER BY AU.USERNAME)TT,AU.USERNAME AS "USUARIO", AU.EMAIL AS "EMAIL",
                    CASE
                        WHEN AU.IS_ACTIVE  = '1' THEN 'ACTIVO'
                        ELSE 'INACTIVO'
                    END AS "ESTADO",
                    TO_CHAR(AU.DATE_JOINED, 'DD-MM-YYYY hh24:mi') AS "FEC CREADO"
                    FROM AUTH_USER AU
                    """)
                    usuarios = cursor.fetchall()
                    cursor.execute("SELECT COUNT(*) FROM AUTH_USER")
                    usuarios_tt = cursor.fetchone()[0]
                    if not usuarios:
                        messages.error(request, 'No se encontró Detalles de Usuarios a Mostrar')
                        return redirect('informes') 
                elif op == "op2" and fd != None and fh != None:
                    try:
                        conn = cx_Oracle.connect('PORTAFOLIO/123@//localhost:1521/xe')
                        output = conn.cursor()
                        cursor = conn.cursor()
                        cursor.callproc('sp_buscarVentas', [fd,fh, output])
                        resultado = output.fetchall()
                        cursor.execute(f"SELECT COUNT(*) FROM DOCUMENTO  WHERE TO_CHAR(FECHA_EMISION,'YYYY-MM-DD') BETWEEN '{fd}' AND '{fh}' ")
                        doc_tt = cursor.fetchone()[0]
                        cursor.execute(f"""
                        SELECT COUNT(*)CANTFE, SUM(MONTO_TOTAL) TTFE
                            FROM DOCUMENTO WHERE CODIGO_SII = 33
                            AND TO_CHAR(FECHA_EMISION,'YYYY-MM-DD') BETWEEN '{fd}' AND '{fh}' 
                        """)
                        facturas = cursor.fetchone()
                      
                        cursor.execute(f"""
                        SELECT COUNT(*)CANTFE, SUM(MONTO_TOTAL) TTFE
                            FROM DOCUMENTO WHERE CODIGO_SII = 61
                            AND TO_CHAR(FECHA_EMISION,'YYYY-MM-DD') BETWEEN '{fd}' AND '{fh}'                             
                        """)                        
                        notacreditos = cursor.fetchone()
                        totalIng = (facturas[1] - notacreditos[1])
                        formato = '%Y-%m-%d'
                        fechaD = datetime.strptime(fd,formato )
                        fechaH = datetime.strptime(fh,formato )
                        print(resultado)
                        if not resultado:
                            messages.error(request, 'No existe Detalle de Ventas en Rango de Fecha Buscado')
                            return redirect('informes') 
                    except Exception as e:
                        print(e)
                    else:
                        print('ejecutado')
                    finally:
                        conn.close()
                elif op == "op3" and fd != None and fh != None:
                    cursor.execute(f"""
                    SELECT ROW_NUMBER() OVER (ORDER BY TO_CHAR(OC.FECHA_EMISION, 'DD-MM-YYYY'))TT, OC.ID_ORDEN_DE_COMPRA AS "NRO_OC", 
                        C.RUT_EMPRESA, C.DV, C.RAZON_SOCIAL,
                        TO_CHAR(OC.FECHA_EMISION, 'DD-MM-YYYY') AS FEC_EMISION, NVL(OC.MONTO_TOTAL,0), 
                        OC.CANT_HUESPED
                    FROM ORDEN_COMPRA OC
                    JOIN CLIENTE C ON OC.ID_CLIENTE = C.ID_CLIENTE
                    WHERE  TO_CHAR(OC.FECHA_EMISION, 'YYYY-MM-DD') BETWEEN '{fd}' AND '{fh}'
                    """)
                    ordenes_compras = cursor.fetchall()
                    cursor.execute(f"SELECT COUNT(*) TT, SUM(MONTO_TOTAL) MONTOTT FROM ORDEN_COMPRA  WHERE TO_CHAR(FECHA_EMISION,'YYYY-MM-DD') BETWEEN '{fd}' AND '{fh}' ")
                    doc_tt = cursor.fetchone()
                    print(doc_tt)
                    formato = '%Y-%m-%d'
                    fechaD = datetime.strptime(fd,formato )
                    fechaH = datetime.strptime(fh,formato )
                    if not ordenes_compras:
                            messages.error(request, 'No existe Ordenes de Compra en Rango de Fecha Buscado')
                            return redirect('informes')                         
                else:
                    messages.error(request, 'La Opción de Informe ingresada No existe')
                    return redirect('informes') 
            except Exception as e:
                print(e)
                pass    
    data = {
        'usuarios':usuarios,
        'usuarios_tt':usuarios_tt,
        'resultado':resultado,
        'doc_tt':doc_tt,
        'fechaD':fechaD,
        'fechaH':fechaH,
        'ordenes_compras':ordenes_compras,
        'facturas':facturas,
        'notacreditos':notacreditos,
        'totalIng':totalIng
    }                    
    return render(request, 'Empleados/Informes/print_informe.html',data)
