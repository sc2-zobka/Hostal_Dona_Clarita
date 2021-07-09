# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_cliente = models.BooleanField(default=False)
    is_empleado = models.BooleanField(default=False)
    is_proveedor = models.BooleanField(default=False)
    imagen = models.CharField(max_length=100, null=True)
    # Preguntar si la multiempresa sera tipo ERP o no

    class Meta:
        db_table = 'auth_user'


class Accesorio(models.Model):
    id_accesorio = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=20)
    estatus = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'accesorio'


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)
    estatus = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'categoria'


class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    estatus = models.CharField(max_length=1)
    razon_social = models.CharField(max_length=100)
    rut_empresa = models.BigIntegerField()
    dv = models.CharField(max_length=1)
    id_usuario = models.ForeignKey('User', models.DO_NOTHING, db_column='id', blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    comuna = models.ForeignKey('Comuna', models.DO_NOTHING, blank=True, null=True)
    celular = models.BigIntegerField(blank=True, null=True)
    nombre_comercial = models.CharField(max_length=100, blank=True, null=True)
    id_tipo_cliente = models.ForeignKey('TipoCliente', models.DO_NOTHING, db_column='id_tipo_cliente')
    codigo = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = 'cliente'


class Comuna(models.Model):
    comuna_id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)
    id_region = models.ForeignKey('Region', models.DO_NOTHING, db_column='id_region')

    class Meta:
        managed = False
        db_table = 'comuna'


class Configuracion(models.Model):
    rut_empresa = models.AutoField(primary_key=True)
    dv = models.CharField(max_length=1)
    nombre_empresa = models.CharField(max_length=100)
    logo_empresa = models.CharField(max_length=100, blank=True, null=True)
    favicon = models.CharField(max_length=100, blank=True, null=True)
    razon_social = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)
    id_usuario = models.ForeignKey('User', models.DO_NOTHING, db_column='id', blank=True, null=True)
    comuna = models.ForeignKey(Comuna, models.DO_NOTHING)
    divisa_principal = models.CharField(max_length=3, blank=True, null=True)
    divisa_secundaria = models.CharField(max_length=3, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'configuracion'


class DetalleOrdenCompra(models.Model):
    id_detalle_orden_de_compra = models.AutoField(primary_key=True)
    id_orden_de_compra = models.ForeignKey('OrdenCompra', models.DO_NOTHING, db_column='id_orden_de_compra')
    inicio_estadia = models.DateField()
    final_estadia = models.DateField()
    monto = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'detalle_orden_compra'


class DetalleOrdenPedido(models.Model):
    id_detalle_pedido = models.AutoField(primary_key=True)
    cantidad = models.BigIntegerField()
    id_orden_pedido = models.ForeignKey('OrdenPedido', models.DO_NOTHING, db_column='id_orden_pedido')
    id_producto = models.ForeignKey('Producto', models.DO_NOTHING, db_column='id_producto')

    class Meta:
        managed = False
        db_table = 'detalle_orden_pedido'


class DetalleServicioAdicional(models.Model):
    id_det_serv_adic = models.AutoField(primary_key=True)
    id_detalle_orden_de_compra = models.ForeignKey(DetalleOrdenCompra, models.DO_NOTHING, db_column='id_detalle_orden_de_compra', blank=True, null=True)
    id_servicio = models.ForeignKey('ServicioAdicional', models.DO_NOTHING, db_column='id_servicio')

    class Meta:
        managed = False
        db_table = 'detalle_servicio_adicional'


class Documento(models.Model):
    id_documento = models.AutoField(primary_key=True)
    fecha_emision = models.DateField()
    monto_neto = models.BigIntegerField()
    iva = models.BigIntegerField()
    monto_total = models.BigIntegerField()
    id_estatus_documento = models.ForeignKey('EstatusDocumento', models.DO_NOTHING, db_column='id_estatus_documento')
    id_orden_de_compra = models.ForeignKey('OrdenCompra', models.DO_NOTHING, db_column='id_orden_de_compra', blank=True, null=True)
    id_orden_pedido = models.ForeignKey('OrdenPedido', models.DO_NOTHING, db_column='id_orden_pedido', blank=True, null=True)
    codigo_sii = models.ForeignKey('TipoDocumento', models.DO_NOTHING, db_column='codigo_sii')
    fecha_anulacion = models.DateField(blank=True, null=True)
    doc_anulado = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'documento'


class Empleado(models.Model):
    id_empleado = models.AutoField(primary_key=True)
    rut_empleado = models.BigIntegerField()
    dv = models.CharField(max_length=1)
    nombres = models.CharField(max_length=100)
    apellido_p = models.CharField(max_length=50)
    apellido_m = models.CharField(max_length=50)
    nacimiento = models.DateField()
    celular = models.BigIntegerField(blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    nacionalidad = models.CharField(max_length=50, blank=True, null=True)
    comuna = models.ForeignKey(Comuna, models.DO_NOTHING, blank=True, null=True)
    id_usuario = models.ForeignKey('User', models.DO_NOTHING, db_column='id', blank=True, null=True)
    pedidos = models.CharField(max_length=1)
    estatus = models.CharField(max_length=1)
    id_tipo = models.ForeignKey('TipoEmpleado', models.DO_NOTHING, db_column='id_tipo')

    class Meta:
        managed = False
        db_table = 'empleado'


class EstadoHabitacion(models.Model):
    id_estado_habitacion = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'estado_habitacion'


class EstatusDocumento(models.Model):
    id_estatus_documento = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'estatus_documento'


class EstatusOrdenCompra(models.Model):
    id_estatus_orden_compra = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'estatus_orden_compra'


class EstatusOrdenPedido(models.Model):
    id_estatus_orden_pedido = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'estatus_orden_pedido'


class EstatusRecepcion(models.Model):
    id_estatus_recep = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'estatus_recepcion'


class Habitacion(models.Model):
    id_habitacion = models.AutoField(primary_key=True)
    numero_habitacion = models.BigIntegerField()
    precio = models.BigIntegerField()
    descripcion = models.CharField(max_length=200)
    id_estado_habitacion = models.ForeignKey(EstadoHabitacion, models.DO_NOTHING, db_column='id_estado_habitacion')
    id_tipo_habitacion = models.ForeignKey('TipoHabitacion', models.DO_NOTHING, db_column='id_tipo_habitacion')
    imagen = models.CharField(max_length=100)
    estado = models.CharField(max_length=1)
    muestra_menu = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'habitacion'


class HabitacionAccesorio(models.Model):
    id_hab_acce = models.AutoField(primary_key=True)
    id_tipo_habitacion = models.ForeignKey('TipoHabitacion', models.DO_NOTHING, db_column='id_tipo_habitacion')
    id_accesorio = models.ForeignKey(Accesorio, models.DO_NOTHING, db_column='id_accesorio')

    class Meta:
        managed = False
        db_table = 'habitacion_accesorio'


class Huesped(models.Model):
    id_huesped = models.AutoField(primary_key=True)
    rut = models.BigIntegerField()
    dv = models.CharField(max_length=1)
    nombre = models.CharField(max_length=100)
    apellido_p = models.CharField(max_length=50)
    apellido_m = models.CharField(max_length=50)
    email = models.CharField(max_length=50, blank=True, null=True)
    telefono = models.BigIntegerField(blank=True, null=True)
    id_cliente = models.ForeignKey(Cliente, models.DO_NOTHING, db_column='id_cliente')
    fecha_nacimiento = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'huesped'


class OrdenCompra(models.Model):
    id_orden_de_compra = models.AutoField(primary_key=True)
    fecha_emision = models.DateField()
    monto_neto = models.BigIntegerField(blank=True, null=True)
    iva = models.BigIntegerField(blank=True, null=True)
    monto_total = models.BigIntegerField(blank=True, null=True)
    cant_huesped = models.BigIntegerField()
    id_cliente = models.ForeignKey(Cliente, models.DO_NOTHING, db_column='id_cliente')
    id_estatus_orden_compra = models.ForeignKey(EstatusOrdenCompra, models.DO_NOTHING, db_column='id_estatus_orden_compra')

    class Meta:
        managed = False
        db_table = 'orden_compra'


class OrdenPedido(models.Model):
    id_orden_pedido = models.AutoField(primary_key=True)
    fecha_emision = models.DateField()
    id_estatus_orden_pedido = models.ForeignKey(EstatusOrdenPedido, models.DO_NOTHING, db_column='id_estatus_orden_pedido')
    id_cliente = models.ForeignKey(Cliente, models.DO_NOTHING, db_column='id_cliente')
    id_empleado = models.ForeignKey(Empleado, models.DO_NOTHING, db_column='id_empleado')
    observacion = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orden_pedido'


class Pais(models.Model):
    id_pais = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'pais'


class PlatoSemanal(models.Model):
    id_comedor = models.AutoField(primary_key=True)
    id_tipo_comedor = models.ForeignKey('TipoComedor', models.DO_NOTHING, db_column='id_tipo_comedor')
    descripcion = models.CharField(max_length=100)
    dia_desde = models.DateField()
    dia_hasta = models.DateField()
    imagen = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'plato_semanal'


class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    especificacion = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)
    precio = models.BigIntegerField()
    stock = models.BigIntegerField()
    stock_critico = models.BigIntegerField()
    fecha_vencimiento = models.DateField(blank=True, null=True)
    id_categoria = models.ForeignKey(Categoria, models.DO_NOTHING, db_column='id_categoria')
    id_tipo_producto = models.ForeignKey('TipoProducto', models.DO_NOTHING, db_column='id_tipo_producto')
    estado = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'producto'


class RecepcionOrdenPedido(models.Model):
    id_registro_pedido = models.AutoField(primary_key=True)
    fecha_entrega = models.DateField()
    id_orden_pedido = models.BigIntegerField()
    id_estatus_recep = models.ForeignKey(EstatusRecepcion, models.DO_NOTHING, db_column='id_estatus_recep')
    observacion = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'recepcion_orden_pedido'


class Region(models.Model):
    id_region = models.AutoField(primary_key=True)
    reg_cod = models.CharField(max_length=10)
    descripcion = models.CharField(max_length=100)
    id_pais = models.ForeignKey(Pais, models.DO_NOTHING, db_column='id_pais')

    class Meta:
        managed = False
        db_table = 'region'


class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    id_detalle_orden_de_compra = models.ForeignKey(DetalleOrdenCompra, models.DO_NOTHING, db_column='id_detalle_orden_de_compra')
    check_in = models.CharField(max_length=1, blank=True, null=True)
    id_habitacion = models.ForeignKey(Habitacion, models.DO_NOTHING, db_column='id_habitacion')
    plato = models.BigIntegerField(blank=True, null=True)
    id_tipo_comedor = models.ForeignKey('TipoComedor', models.DO_NOTHING, db_column='id_tipo_comedor')
    id_huesped = models.ForeignKey(Huesped, models.DO_NOTHING, db_column='id_huesped')

    class Meta:
        managed = False
        db_table = 'reserva'


class ServicioAdicional(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=50)
    precio = models.BigIntegerField()
    mostrar_inicio = models.CharField(max_length=1)
    imagen = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'servicio_adicional'


class TipoCliente(models.Model):
    id_tipo_cliente = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'tipo_cliente'


class TipoComedor(models.Model):
    id_tipo_comedor = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)
    estado = models.CharField(max_length=1)
    precio = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'tipo_comedor'


class TipoDocumento(models.Model):
    codigo_sii = models.CharField(primary_key=True, max_length=2)
    descripcion = models.CharField(max_length=40, blank=True, null=True)
    abreviado = models.CharField(max_length=3)
    estado = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'tipo_documento'


class TipoEmpleado(models.Model):
    id_tipo = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)
    estatus = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'tipo_empleado'


class TipoHabitacion(models.Model):
    id_tipo_habitacion = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)
    estado = models.CharField(max_length=1)
    capacidad = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'tipo_habitacion'


class TipoMoneda(models.Model):
    codigo_moneda = models.CharField(primary_key=True, max_length=3)
    descripcion = models.CharField(max_length=20, blank=True, null=True)
    valor_conversion = models.BigIntegerField()
    valor_peso = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estado = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'tipo_moneda'


class TipoProducto(models.Model):
    id_tipo_producto = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)
    estado = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_producto'

class Opinion(models.Model):
    id_opinion = models.AutoField(primary_key=True)
    id_orden_de_compra = models.ForeignKey('OrdenCompra', models.DO_NOTHING, db_column='id_orden_de_compra')
    observacion = models.CharField(max_length=500, blank=True, null=True)

