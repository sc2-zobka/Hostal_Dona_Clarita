from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from Aplicaciones.app.models import User, Cliente
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.models import Group
from .forms import CustomUserCreationForm, CustomEmpleadoCreationForm
from django.db import connection, connections, transaction
from django.contrib import auth
from django.core.files.storage import FileSystemStorage
import os
# Create your views here.


def login_new(request):
    mensaje = ''
    user_db = ''
    if request.method == "POST":
        username = request.POST['username']
        pwd = request.POST['password']
        username = username.strip().lower()
        pwd = pwd.strip().lower()
        if len(username) == 0 and len(pwd) == 0:
            messages.warning(
                request, 'Usuario y Contraseña son Campos Obligatorios. Complételos para Continuar')
        elif len(username) == 0:
            messages.warning(
                request, 'El Campo Usuario es Obligatorio. Complételo para Continuar')
        elif len(pwd) == 0:
            messages.warning(
                request, 'El Campo Contraseña es Obligatorio. Complételo para Continuar')
        else:
            try:
                user_db = User.objects.get(username=username)
                if user_db is not None:
                    user = auth.authenticate(username=username, password=pwd)
                    print(user)
                    if user:
                        if user is not None and user.is_active:
                            auth.login(request, user)
                            if user.is_cliente:
                                print('es cliente')
                                with connection.cursor() as cursor:
                                    try:
                                        cursor.execute(
                                            "SELECT * FROM APP_CLIENTE WHERE USUARIO_ID = %s", [user.id])
                                        cliente = cursor.fetchone()
                                        print(cliente)

                                        if cliente[1] == 1:
                                            return redirect('/dashboard')
                                        else:
                                            messages.error(
                                                request, '¡Usuario o Contraseña Incorrecta! El usuario o contraseña ingresados NO existe en la Base de Datos.')
                                    except:
                                        pass
                                        messages.error(
                                            request, '¡Usuario o Contraseña Incorrecta! El usuario o contraseña ingresados NO existe en la Base de Datos.')
                            elif user.is_empleado:
                                print('es empleado')
                                return redirect('/dashboard')
                            elif user.is_proveedor:
                                print('es proveedor')
                                return redirect('/dashboard')
                            elif user.is_superuser and user.is_active:
                                print('es administrador')
                                return redirect('/dashboard')
                        else:
                            messages.error(
                                request, 'El Usuario está Desactivado')

                    else:
                        messages.error(
                            request, 'El Usuario o Contraseña son Incorrectos. Verifique e intente de Nuevo')
            except:
                messages.error(
                    request, '¡Usuario o Contraseña Incorrecta! El usuario o contraseña ingresados NO existe en la Base de Datos.')
                pass
    data = {
        'mensaje': mensaje,
    }
    return render(request, 'appADM/register/login.html', data)


def registro(request):
    mensaje = ''
    dataForm = ''
    rut = ''
    rut2 = ''
    vrutSinDv = ''
    perfil_db = ''
    razon_social = ''
    nombre_usuario = ''
    email = ''
    if request.method == "POST":
        rut = request.POST['rut']
        if len(rut) == 0:
            messages.error(
                request, 'El Campo Rut es Obligatorio. Complételos para Continuar')
            mensaje = 'rut vacio'
        elif len(rut) > 0:
            # Guarda variable a pasar
            vrut = rut
            # Limpia Rut de Puntos y Guión
            rut2 = rut.replace('.', "")
            rut2 = rut2.replace('-', "")
            # Quita Digito Verificador
            vrutSinDv = rut2.rstrip(rut2[-1])
            # Obtiene Digito Verificador
            dv = rut2[-1]
            cliente_reactivado = False
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        f"SELECT COUNT(*)TT FROM APP_CLIENTE WHERE RUT_EMPRESA = '{vrutSinDv}' AND DV = '{dv}'")
                    tipo_cliente = cursor.fetchone()
                    if tipo_cliente[0] > 0:
                        messages.error(
                            request, 'El Rut ya pertenece a un Usuario de Hostal Doña Clarita')
                        rut = 0
                except:
                    pass
            try:
                perfil_db = Cliente.objects.get(rut_empresa=vrutSinDv)
                if perfil_db.estatus == 0:
                    cliente_reactivado = True
                    raise ValueError('Cliente se encuentra desactivado')
            except:
                pass
                try:
                    # Captura de Datos en variables
                    razon_social = request.POST['nombre']
                    nombre_usuario = request.POST['username']
                    email = request.POST['email']
                    ipass = request.POST['password1']
                    ipasscon = request.POST['password2']
                    # Limpieza de Espacios
                    razon_social = razon_social.strip()
                    nombre_usuario = nombre_usuario.strip()
                    email = email.strip().lower()
                    ipass = ipass.strip()
                    ipasscon = ipasscon.strip()
                    if len(razon_social) == 0 and len(nombre_usuario) == 0 and len(email) == 0 and len(ipass) == 0 and len(ipasscon) == 0:
                        messages.warning(
                            request, 'Todos los Campos son Obligatorios. Complételos para Continuar')
                    # Validación de Campos Vacios
                    if len(razon_social) == 0:
                        messages.warning(
                            request, 'El Campo Razón Social es Obligatorio. Complételo para Continuar')
                    elif len(nombre_usuario) == 0:
                        messages.warning(
                            request, 'El Campo Nombre de Usuario es Obligatorio. Complételo para Continuar')
                    elif len(email) == 0:
                        messages.warning(
                            request, 'El Campo Email es Obligatorio. Complételo para Continuar')
                    elif len(ipass) == 0:
                        messages.warning(
                            request, 'El Campo Contraseña es Obligatorio. Complételo para Continuar')
                    elif len(ipasscon) == 0:
                        messages.warning(
                            request, 'El Campo Confirmar Contraseña es Obligatorio. Complételo para Continuar')
                    # validación de largo contraseñas
                    elif len(ipass) < 8 or len(ipass) < 8:
                        messages.warning(
                            request, 'La Contraseña debe tener un largo Mínimo de 8 caracteres. Complételo para Continuar')
                    else:
                        # Validación de contraseñas
                        if ipass != ipasscon:
                            messages.error(
                                request, 'Las Contraseñas NO son identicas')
                        else:
                            # Valida que todos los campos se cumplan
                            if len(razon_social) > 0 and len(nombre_usuario) > 0 and len(email) > 0 and len(ipass) > 0 and len(ipasscon) > 0 and ipass == ipasscon:
                                with connection.cursor() as cursor:
                                    cursor.execute(f"""SELECT COUNT(*)TT FROM AUTH_USER WHERE EMAIL = '{email}'""")
                                    validaEmail = cursor.fetchone()
                                    if validaEmail[0] >0:
                                        messages.error(request, 'El Email ya pertenece a un Usuario de Hostal Doña Clarita')
                                    else:
                                        dataForm = {
                                            "form": CustomUserCreationForm()
                                        }
                                        formulario = CustomUserCreationForm(
                                            data=request.POST)

                                        if formulario.is_valid() or cliente_reactivado:
                                            user_db = None

                                            if not cliente_reactivado:
                                                #
                                                # Se guarda registro en la base de datos con la clave encriptada de Django
                                                #
                                                formulario.save()
                                                user = authenticate(
                                                    username=formulario.cleaned_data["username"],
                                                    password=formulario.cleaned_data["password1"])
                                                #
                                                # Setear el grupo de usuario cliente
                                                #
                                                group = Group.objects.filter(
                                                    name__iexact='Cliente').first()

                                                #
                                                # Obtener tipo cliente
                                                #
                                                tipo_cliente = 0
                                                with connection.cursor() as cursor:
                                                    try:
                                                        cursor.execute(
                                                            "SELECT ID FROM APP_TIPOCLIENTE WHERE DESCRIPCION = %s", ['Cliente'])
                                                        tipo_cliente = cursor.fetchone()[
                                                            0]
                                                    except:
                                                        pass
                                                user_db = User.objects.get(pk=user.id)
                                                user_db.groups.add(group)
                                                user_db.is_cliente = True
                                                user_db.email = email
                                                #user_db.last_name = apellido
                                                user_db.save()
                                            else:
                                                user_db = User.objects.get(
                                                    pk=perfil_db.usuario_id)
                                                user_db.is_cliente = True
                                                user_db.email = email
                                                #user_db.last_name = apellido
                                                user_db.save()

                                            #
                                            # Setear el Perfil de cliente
                                            #
                                            with connection.cursor() as cursor:
                                                try:
                                                    if not cliente_reactivado:
                                                        cursor.execute("INSERT INTO APP_CLIENTE(ESTATUS, RAZON_SOCIAL, RUT_EMPRESA,"
                                                                    "DV, TIPO_CLIENTE_ID, USUARIO_ID) VALUES (%s, %s, %s, %s, %s, %s)",
                                                                    [1, razon_social, vrutSinDv, dv, tipo_cliente, user_db.id])
                                                    else:
                                                        cursor.execute("UPDATE APP_CLIENTE SET ESTATUS = %s, RAZON_SOCIAL = %s"
                                                                    "WHERE USUARIO_ID = %s",
                                                                    [1, razon_social, user_db.id])

                                                    mensaje = 'ok'
                                                    messages.success(
                                                        request, 'Cliente Registrado Correctamente. Ya puede Iniciar sesión')
                                                    return redirect(to="login_new")
                                                except Exception as e:
                                                    print(e)
                                                    pass
                                        else:
                                            for i in formulario.errors:
                                                if i == 'username':
                                                    messages.error(
                                                        request, 'El Usuario Ingresado Ya existe. Verifique e Intente de Nuevo')
                                                elif i == 'password2':
                                                    messages.error(
                                                        request, 'La Contraseña es Demasiado identica al Correo y/o Nombre de Usuario')

                except Exception as e:
                    print(e)
                    pass

    data = {
        'mensaje': mensaje,
        'dataForm': dataForm,
        'vrut': rut,
        'razon_social': razon_social,
        'nombre_usuario': nombre_usuario,
        'email': email,
    }

    return render(request, 'appADM/register/registro.html', data)




def config_user(request):
    cliente = ''
    region = ''
    comunas = ''
    comuna = ''
    regiones = ''
    nom_fantasia = ''
    direccion = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"""
             SELECT C.USUARIO_ID,(C.RUT_EMPRESA ||'-'|| C.DV) AS RUT,C.RAZON_SOCIAL, C.NOMBRE_COMERCIAL, AU.USERNAME,  AU.EMAIL, C.CELULAR, 
                        C.ESTATUS, C.COMUNA_ID, C.DIRECCION, AU.LAST_LOGIN AS '10'
                        FROM APP_CLIENTE C
                        JOIN AUTH_USER AU ON C.USUARIO_ID = AU.ID
                        WHERE C.USUARIO_ID = {request.user.id} 
            """)            
            cliente = cursor.fetchone()
            
            if cliente[3]:
                nom_fantasia = cliente[3].strip()
            if cliente[9]:
                direccion = cliente[9].strip()
            cursor.execute("SELECT * FROM APP_COMUNA")
            comunas = cursor.fetchall()

            cursor.execute("SELECT * FROM APP_REGION")
            regiones = cursor.fetchall()

            if cliente[8] is not None:
                cursor.execute("SELECT * FROM APP_COMUNA WHERE ID = %s", [cliente[8]])
                comuna = cursor.fetchone()

                cursor.execute("SELECT * FROM APP_REGION WHERE ID = %s", [comuna[2]])
                region = cursor.fetchone()
                print(region)
        except Exception as e:
            print(e)
            pass

    data = {
        'cliente': cliente,
        'regiones': regiones,
        'region': region,
        'comunas': comunas,
        'comuna': comuna,
        'nom_fantasia':nom_fantasia,
        'direccion':direccion
    }

    if request.method == 'POST':
        razon_social = request.POST['r_social']
        nombre_comercial = request.POST['nom_fantasia']
        email = request.POST['email']
        telefono = request.POST['fono']
        region = request.POST.get('reg_sel', None)
        comuna = request.POST.get('com_sel', None)
        direccion = request.POST['direccion']

        razon_social = razon_social.strip().lower()
        nombre_comercial = nombre_comercial.strip().lower()
        email = email.strip().lower()
        telefono = telefono.strip().lower()
        region = region.strip().lower()
        comuna = comuna.strip().lower()
        direccion = direccion.strip().lower()

        if len(razon_social) >0 and len(nombre_comercial) >=0 and len(email) >0 and len(telefono) >=0 and len(comuna) > 0 and len(direccion) >0:
            user_db = request.user
            if len(email) > 0:
                user_db.email = email
                user_db.first_name = razon_social
                user_db.save()
            
            with connection.cursor() as cursor:
                try:
                    cursor.execute("UPDATE APP_CLIENTE SET RAZON_SOCIAL = %s, " \
                        "DIRECCION = %s, " \
                        "CELULAR = %s, " \
                        "NOMBRE_COMERCIAL = %s, " \
                        "COMUNA_ID = %s " \
                        "WHERE USUARIO_ID = %s", [razon_social, direccion, telefono, nombre_comercial, comuna, user_db.id])
                                    
                    messages.success(request, f' Se ha Modificado correctamente')
                    return redirect('config-user')
                except Exception as e:
                    print(e)
                    pass
        else:
            messages.error(request, f'Complete Campos Obligatorios! estos se identifican con (*)')
    return render(request, 'appADM/config-user.html', data)

def pass_user(request):
    mensaje = str()

    if request.method == "POST":
        actual_pwd = request.POST["act_pwd"]
        nueva_pwd = request.POST["new_pwd"]
        confirmar_pwd = request.POST["conf_new_pwd"]
        actual_pwd.strip().lower()
        nueva_pwd.strip().lower()
        confirmar_pwd.strip().lower()
        user_db = request.user
        if user_db:
            user = auth.authenticate(username=user_db, password=actual_pwd)
            if user:
                if len(actual_pwd) > 0 and len(nueva_pwd) >= 8 and len(confirmar_pwd) >= 8:
                    if nueva_pwd == confirmar_pwd:
                        usuario = request.user
                        usuario.set_password(nueva_pwd)
                        usuario.save()
                        messages.success(request, f' Se ha Modificado correctamente')
                        return redirect('pass-user')
                    else:
                        messages.error(request, 'La Contraseña Nueva Ingresada No es Identica a la Confirmación, Corrija e Intente de Nuevo')
                       
                else:
                    messages.error(request, 'El Largo de La Contraseña es mínimo de 8 caracteres') 
            else:
                messages.error(request, 'Contraseña Actual Incorrecta') 
        else:
            return redirect('pass-user')                    

    data = {
        'mensaje': mensaje,
    }

    return render(request, 'appADM/pass-user.html', data)        


def config_emp(request):
    usuario = ''
    region = ''
    comunas = ''
    comuna = ''
    regiones = ''
    apellido_ma = ''
    direccion = ''
    fecha = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"""
             SELECT E.USUARIO_ID AS '0',(E.RUT_EMPLEADO ||'-'|| E.DV) AS '1',E.NOMBRES AS '2', E.APELLIDO_P AS '3', E.APELLIDO_M AS '4',
                AU.USERNAME AS '5', AU.EMAIL AS '6', E.CELULAR AS '7', 
                E.NACIMIENTO AS '8', E.NACIONALIDAD AS '9', E.COMUNA_ID AS '10', E.DIRECCION AS '11', AU.LAST_LOGIN AS '12'
            FROM APP_EMPLEADO E
            JOIN AUTH_USER AU ON E.USUARIO_ID = AU.ID
            WHERE E.USUARIO_ID = {request.user.id} 
            """)      
            usuario = cursor.fetchone()
            formato = '%Y-%m-%d'
            fechaT = usuario[8]
            if fechaT:
                fecha = fechaT.strftime(formato)
            if usuario[4]:
                apellido_ma = usuario[4].strip()
            if usuario[11]:
                direccion = usuario[11].strip()
            cursor.execute("SELECT * FROM APP_COMUNA")
            comunas = cursor.fetchall()

            cursor.execute("SELECT * FROM APP_REGION")
            regiones = cursor.fetchall()

            if usuario[10] is not None:
                cursor.execute("SELECT * FROM APP_COMUNA WHERE ID = %s", [usuario[10]])
                comuna = cursor.fetchone()
                cursor.execute("SELECT * FROM APP_REGION WHERE ID = %s", [comuna[2]])
                region = cursor.fetchone()
                print(region)
        except Exception as e:
            print(e)
            pass

    data = {
        'usuario': usuario,
        'regiones': regiones,
        'region': region,
        'comunas': comunas,
        'comuna': comuna,
        'apellido_ma':apellido_ma,
        'direccion':direccion,
        'fecha':fecha
    }

    if request.method == 'POST':
        email = request.POST['email']
        nombres = request.POST['nombres']
        apellido_p = request.POST['apellido_p']
        apellido_m = request.POST['apellido_m']
        fec_nac = request.POST['fec_nac']
        nacionalidad = request.POST['nacionalidad']
        telefono = request.POST['fono']
        comuna = request.POST.get('com_sel', None)
        direccion = request.POST['direccion']
        nombres = nombres.strip()
        apellido_p = apellido_p.strip()
        apellido_m = apellido_m.strip()
        email = email.strip().lower()
        telefono = telefono.strip()
        fec_nac = fec_nac.strip()
        nacionalidad = nacionalidad.strip().lower()
        comuna = comuna.strip()
        direccion = direccion.strip().lower()

        if len(nombres) >0 and len(apellido_p) >0 and len(apellido_m) >=0 and len(email) >0  and len(comuna) > 0 and len(direccion) >0:
            user_db = request.user
            if len(email) > 0:
                user_db.email = email
                user_db.first_name = nombres
                user_db.last_name = apellido_p
                user_db.save()
            
            with connection.cursor() as cursor:
                try:
                    cursor.execute(f"""UPDATE APP_EMPLEADO SET NOMBRES = '{nombres}',
                        APELLIDO_P ='{apellido_p}', APELLIDO_M = '{apellido_m}' , CELULAR = '{telefono}',
                        NACIMIENTO = '{fec_nac}', NACIONALIDAD = '{nacionalidad}', DIRECCION = '{direccion}',                                               
                        COMUNA_ID = '{comuna}' 
                        WHERE USUARIO_ID = '{user_db.id}'""")
                    messages.success(request, f' Se ha Modificado correctamente')
                    return redirect('config-emp')
                except Exception as e:
                    print(e)
                    pass
        else:
            messages.error(request, f'Complete Campos Obligatorios! estos se identifican con (*)')
    return render(request, 'appADM/config-emp.html', data)

# ***Módulo:Empleados*** Opción: configuraciones empresa


def config(request):
    region = ''
    comunas = ''
    comuna = ''
    regiones = ''
    apellido_ma = ''
    direccion = ''
    fecha = ''
    tipo_monedas = ''
    divisa_primaria = ''
    divisa_secundaria = ''
    divisas = ''
    img_logo = ''
    nom_logo = ''
    img_favicon = ''
    nom_favicon = ''
    logo_url = ''
    favicon_url = ''
    imagen = ''
    nom = ''
    imagen2 = ''
    nom2 = ''    
    with connection.cursor() as cursor:
        try:
            cursor.execute("""SELECT * FROM APP_TIPOMONEDA """)
            tipo_monedas = cursor.fetchall()
            cursor.execute(f"""
                SELECT RUT_EMPRESA AS '0', (RUT_EMPRESA ||'-'||DV) AS '1', RAZON_SOCIAL AS '2' ,
                       NOMBRE_EMPRESA AS '3', COMUNA_ID AS '4', DIRECCION AS '5', DIVISA_PRINCIPAL AS '6', 
                       DIVISA_SECUNDARIA AS '7', LOGO_EMPRESA AS '8' , FAVICON AS '9'                          
                FROM APP_CONFIGURACION WHERE RUT_EMPRESA = '6096718'
            """)      
            empresa = cursor.fetchone()
            print(empresa)
            cursor.execute("SELECT * FROM APP_COMUNA")
            comunas = cursor.fetchall()

            cursor.execute("SELECT * FROM APP_REGION")
            regiones = cursor.fetchall()

            if empresa[4] is not None:
                cursor.execute("SELECT * FROM APP_COMUNA WHERE ID = %s", [empresa[4]])
                comuna = cursor.fetchone()
                cursor.execute("SELECT * FROM APP_REGION WHERE ID = %s", [comuna[2]])
                region = cursor.fetchone()
            if empresa[6] is not None:
                cursor.execute("SELECT * FROM APP_TIPOMONEDA WHERE CODIGO_MONEDA = %s", [empresa[6]])
                divisa_primaria = cursor.fetchone()     
            if empresa[7] is not None:
                cursor.execute("SELECT * FROM APP_TIPOMONEDA WHERE  CODIGO_MONEDA= %s", [empresa[7]])
                divisa_secundaria = cursor.fetchone()  
            cursor.execute(f"SELECT * FROM APP_TIPOMONEDA WHERE ESTADO = 1 ")
            divisas = cursor.fetchall()  
            
        except Exception as e:
            print(e)
            pass



    if request.method == 'POST':
        r_social = request.POST['r_social']
        nom_fantasia = request.POST['nom_fantasia']
        comuna_sel = request.POST['com_sel']
        div_primera = request.POST['div_primera']
        div_segunda = request.POST['div_segunda']
        direccion = request.POST['direccion']
        r_social = r_social.strip()
        nom_fantasia = nom_fantasia.strip()
        comuna_sel = comuna_sel.strip()
        try:
            if request.FILES['image'] and request.FILES['imagen'] :
                print(' hay imagen')
                imagen = request.FILES['image']
                nom = imagen.name
                fs = FileSystemStorage(location='media/Logos/')
                if nom != empresa[8]:
                    if os.path.isfile(f'media/Logos/{nom}'):
                        print('existe')
                        os.remove(f'media/Logos/{nom}')
                        filename = fs.save(imagen.name, imagen)
                        logo_url = fs.url(filename)
                    else:
                        print('no existe')
                        filename = fs.save(imagen.name, imagen)
                        logo_url = fs.url(filename)
                else:
                    if os.path.isfile(f'media/Logos/{empresa[8]}'):
                        print('existe')
                        os.remove(f'media/Logos/{empresa[8]}')
                        filename = fs.save(imagen.name, imagen)
                        logo_url = fs.url(filename)
                    else:
                        print('no existe')
                        filename = fs.save(imagen.name, imagen)
                        logo_url = fs.url(filename)
                imagen2 = request.FILES['imagen']   
                nom2 = imagen2.name
                fs2 = FileSystemStorage(location='media/Favicon/')
                if nom2 != empresa[9]:
                    if os.path.isfile(f'media/Favicon/{nom2}'):
                        print('existe')
                        os.remove(f'media/Favicon/{nom2}')
                        filename2 = fs2.save(imagen2.name, imagen2)
                        favicon_url = fs2.url(filename2)
                    else:
                        print('no existe')
                        filename2 = fs2.save(imagen2.name, imagen2)
                        favicon_url = fs2.url(filename2)
                else:
                    if os.path.isfile(f'media/Favicon/{empresa[9]}'):
                        print('existe')
                        os.remove(f'media/Favicon/{empresa[9]}')
                        filename2 = fs2.save(imagen2.name, imagen2)
                        favicon_url = fs2.url(filename2)
                    else:
                        print('no existe')
                        filename2 = fs2.save(imagen2.name, imagen2)
                        favicon_url = fs2.url(filename2)      
                                         
        except Exception as e:
            nom = empresa[8]
            nom2 = empresa[9]
            print('primera img', e)
            pass
            try:
                if request.FILES['image'] :   
                    print(' hay imagen')
                    imagen = request.FILES['image']
                    nom = imagen.name
                    fs = FileSystemStorage(location='media/Logos/')
                    if nom != empresa[8]:
                        if os.path.isfile(f'media/Logos/{nom}'):
                            print('existe')
                            os.remove(f'media/Logos/{nom}')
                            filename = fs.save(imagen.name, imagen)
                            logo_url = fs.url(filename)
                        else:
                            print('no existe')
                            filename = fs.save(imagen.name, imagen)
                            logo_url = fs.url(filename)
                    else:
                        if os.path.isfile(f'media/Logos/{empresa[8]}'):
                            print('existe')
                            os.remove(f'media/Logos/{empresa[8]}')
                            filename = fs.save(imagen.name, imagen)
                            logo_url = fs.url(filename)
                        else:
                            print('no existe')
                            filename = fs.save(imagen.name, imagen)
                            logo_url = fs.url(filename) 
                    nom2 = empresa[9]  
            except Exception as e:
                print('segunda img', e)
                pass
                try:
                    if request.FILES['imagen']:
                        imagen2 = request.FILES['imagen']   
                        nom2 = imagen2.name
                        fs2 = FileSystemStorage(location='media/Favicon/')
                        if nom2 != empresa[9]:
                            if os.path.isfile(f'media/Favicon/{nom2}'):
                                print('existe')
                                os.remove(f'media/Favicon/{nom2}')
                                filename2 = fs2.save(imagen2.name, imagen2)
                                favicon_url = fs2.url(filename2)
                            else:
                                print('no existe')
                                filename2 = fs2.save(imagen2.name, imagen2)
                                favicon_url = fs2.url(filename2)
                        else:
                            if os.path.isfile(f'media/Favicon/{empresa[9]}'):
                                print('existe')
                                os.remove(f'media/Favicon/{empresa[9]}')
                                filename2 = fs2.save(imagen2.name, imagen2)
                                favicon_url = fs2.url(filename2)
                            else:
                                print('no existe')
                                filename2 = fs2.save(imagen2.name, imagen2)
                                favicon_url = fs2.url(filename2) 
                        nom = empresa[8]  
                except Exception as e:
                    print('tercera img', e)
                    pass                                                                                      
        print(nom)
        print(nom2)
        if len(r_social) >0 and len(nom_fantasia) >0 and len(div_primera) >0 and len(div_segunda) >0  and len(comuna) > 0 and len(direccion) >0:
            if len(nom_logo) > 100 or len(nom_favicon) >100:
                messages.error(
                    request, f'Nombre de Imagen excede el Largo Máximo Permitido de 100 Caracteres, Modifique o elija otra para Continuar')
            else:    
                if nom.endswith(".png") or nom.endswith(".PNG") or nom == '':      
                    if nom2.endswith('.png') or nom2.endswith('.PNG') or nom2.endswith('.ico') or nom2.endswith('.ICO') or nom2 == '':      
                        with connection.cursor() as cursor:
                            try:
                                cursor.execute(f"""UPDATE APP_CONFIGURACION SET RAZON_SOCIAL = '{r_social}',
                                    NOMBRE_EMPRESA ='{nom_fantasia}', DIVISA_PRINCIPAL = '{div_primera}' , DIVISA_SECUNDARIA = '{div_segunda}',
                                    DIRECCION = '{direccion}',                                               
                                    COMUNA_ID = '{comuna_sel}' , LOGO_EMPRESA = '{nom}' , FAVICON = '{nom2}'
                                    WHERE RUT_EMPRESA = '6096718'""")
                                messages.success(request, f' Se ha Modificado correctamente')
                                return redirect('config')
                            except Exception as e:
                                print(e)
                                pass
                    else:
                        messages.error(request, 'El Formato de la imagen del Favicon NO es Valida. Verifique e Intente de Nuevo')
                else:
                    messages.error(request, 'El Formato de la imagen del Logo NO es Valida. Verifique e Intente de Nuevo')

        else:
            messages.error(request, f'Complete Campos Obligatorios! estos se identifican con (*)')
    data = {
        'empresa': empresa,
        'regiones': regiones,
        'region': region,
        'comunas': comunas,
        'comuna': comuna,
        'apellido_ma':apellido_ma,
        'direccion':direccion,
        'fecha':fecha,
        'tipo_monedas':tipo_monedas,
        'divisas':divisas,
        'divisa_primaria':divisa_primaria,
        'divisa_secundaria':divisa_secundaria,
        'logo_url':logo_url,
        'favicon_url':favicon_url
    }
    return render(request, 'AppADM/Configuraciones/config.html', data)


def tipo_moneda(request):
    codigo = ''
    nombre = ''
    valor = ''
    estado = ''
    tipo_moneda = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute("""SELECT * FROM APP_TIPOMONEDA """)
            tipo_moneda = cursor.fetchall()
        except Exception as e:
            print(e)
            pass
    if request.method == "POST":
        codigo = request.POST['codigo']
        nombre = request.POST['nombre']
        estado = request.POST['estado']
        valor = request.POST['valor']
        codigo = codigo.strip().upper()        
        nombre = nombre.strip()  
        if len(codigo) > 0 and len(nombre) > 0 and len(estado) > 0 and len(valor) > 0:
            if len(codigo) != 3:
                messages.error(
                request, f'El Largo del Código debe ser de 3 Caracteres. Verifique e Intente de Nuevo')
            else:
                with connection.cursor() as cursor:
                    try:
                        cursor.execute(
                            "SELECT COUNT(*)TT FROM APP_TIPOMONEDA WHERE DESCRIPCION LIKE %s", [nombre])
                        validaExistencia = cursor.fetchone()
                        if validaExistencia[0] > 0:
                            messages.error(
                                request, f'El Nombre {nombre} ya Pertence a una  Moneda (Divisa)')
                        else:
                            cursor.execute(
                                "SELECT COUNT(*)TT FROM APP_TIPOMONEDA WHERE CODIGO_MONEDA LIKE %s", [codigo])
                            validaExistenciaCod = cursor.fetchone()
                            if validaExistenciaCod[0] > 0:
                                messages.error(
                                    request, f'El Código {nombre} ya Pertence a una Moneda (Divisa)')                            
                            else:
                                cursor.execute(
                                    f"""INSERT INTO APP_TIPOMONEDA (CODIGO_MONEDA, DESCRIPCION,VALOR_CONVERSION, VALOR_PESO, ESTADO)
                                                            VALUES ('{codigo}', '{nombre}',1, '{valor}', '{estado}')""")
                                messages.success(
                                    request, f'Se ha registrado una Nueva Moneda (Divisa) con nombre {nombre}')
                                return redirect('tipo-moneda')
                    except Exception as e:
                        print(e)
                        pass
        else:
            messages.error(
                request, f'Campo Nombre, Precio, Estado y Valor Obligatorios. Completelos para Continuar')
    data = {
        'tipo_moneda': tipo_moneda
    }

    return render(request, 'AppADM/Configuraciones/tipo_moneda.html', data)


def edit_tipo_moneda(request,id):
    codigo = ''
    nombre = ''
    valor = ''
    estado = ''
    tipo_moneda = ''
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"SELECT * FROM APP_TIPOMONEDA WHERE CODIGO_MONEDA = '{id}' AND CODIGO_MONEDA != 'CLP'")
            tipo_moneda = cursor.fetchone()
            moneda = tipo_moneda[3]
            if not tipo_moneda:
                messages.error(
                    request, 'El Tipo de Comedor que desea editar No Existe o fue eliminado')
                return redirect('tipo-moneda')
        except Exception as e:
            print(e)

    if request.method == "POST":
        codigo = request.POST['codigo']
        nombre = request.POST['nombre']
        estado = request.POST['estado']
        valor = request.POST['valor']
        codigo = codigo.strip().upper()        
        nombre = nombre.strip()  
        if len(codigo) > 0 and len(nombre) > 0 and len(estado) > 0 and len(valor) > 0:
            if len(codigo) != 3:
                messages.error(
                request, f'El Largo del Código debe ser de 3 Caracteres. Verifique e Intente de Nuevo')
            else:
                print(id)
                with connection.cursor() as cursor:
                    try:
                        cursor.execute(
                            f"SELECT COUNT(*)TT FROM APP_TIPOMONEDA WHERE DESCRIPCION LIKE '{nombre}' AND CODIGO_MONEDA not like '{id}'")
                        print(f"SELECT COUNT(*)TT FROM APP_TIPOMONEDA WHERE DESCRIPCION LIKE '{nombre}' AND CODIGO_MONEDA not like '{id}'")
                        validaExistencia = cursor.fetchone()
                        if validaExistencia[0] > 0:
                            messages.error(
                                request, f'El Nombre {nombre} ya Pertence a una  Moneda (Divisa)')
                        else:
                            cursor.execute(
                                f"SELECT COUNT(*)TT FROM APP_TIPOMONEDA WHERE CODIGO_MONEDA LIKE '{codigo}' AND CODIGO_MONEDA not like '{id}'")
                            print(f"SELECT COUNT(*)TT FROM APP_TIPOMONEDA WHERE CODIGO_MONEDA LIKE '{codigo}' AND CODIGO_MONEDA not like '{id}'")
                            validaExistenciaCod = cursor.fetchone()
                            if validaExistenciaCod[0] > 0:
                                messages.error(
                                    request, f'El Código {nombre} ya Pertence a una Moneda (Divisa)')                            
                            else:
                                cursor.execute(
                                    f"""UPDATE APP_TIPOMONEDA SET CODIGO_MONEDA = '{codigo}', DESCRIPCION = '{nombre}',
                                                              VALOR_PESO = '{valor}', ESTADO = '{estado}'
                                                              WHERE CODIGO_MONEDA = '{id}'
                                           """)

                                messages.success(
                                    request, f'Se ha Modificado la Moneda (Divisa) con nombre {nombre} Correctamente')
                                return redirect('tipo-moneda')
                    except Exception as e:
                        print(e)
                        pass
        else:
            messages.error(
                request, f'Campo Nombre, Precio, Estado y Valor Obligatorios. Completelos para Continuar')
    data = {
        'tipo_moneda': tipo_moneda,
        'moneda':moneda
    }





    return render(request, 'AppADM/Configuraciones/edit_tipo_moneda.html', data)
