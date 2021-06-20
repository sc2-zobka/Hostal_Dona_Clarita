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

class Configuracion(models.Model):
    nombre_empresa = models.CharField(max_length=100)
    logo_empresa = models.CharField(max_length=100, null=True)
    favicon = models.CharField(max_length=100, null=True)
    razon_social = models.CharField(max_length=100)
    # Multiples empresas se refiere a una ERP?
    rut_empresa = models.IntegerField(primary_key=True)
    dv = models.CharField(max_length=1)
    direccion = models.CharField(max_length=100)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, default=0, null=True)

class TipoMoneda(models.Model):
    codigo_moneda = models.CharField(max_length=3, primary_key=True)
    descripcion = models.CharField(max_length=20, null=True)
    valor_conversion = models.IntegerField()    
    valor_peso = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.BooleanField(default=False)

    def __str__(self):
        return self.codigo_moneda

class MultiMoneda(models.Model):
    rut_empresa = models.ForeignKey(Configuracion, on_delete=models.PROTECT, default=0)
    tipo_moneda = models.ForeignKey(TipoMoneda, on_delete=models.PROTECT, default=0)

class TipoEmpleado(models.Model):
    estatus = models.BooleanField(default=True)
    descripcion = models.CharField(max_length=64)

class Pais(models.Model):
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return self.descripcion

class Region(models.Model):
    reg_cod = models.CharField(max_length=10)
    descripcion = models.CharField(max_length=100)
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, default=0)

    def __str__(self):
        return self.descripcion

class Comuna(models.Model):
    region = models.ForeignKey(Region, on_delete=models.PROTECT, default=0)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return self.descripcion

class Empleado(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    estatus = models.BooleanField(default=True)
    nombres = models.CharField(max_length=64)
    apellido_p = models.CharField(max_length=50)
    apellido_m = models.CharField(max_length=50)
    tipo_empleado = models.ForeignKey(TipoEmpleado, on_delete=models.PROTECT, default=0)
    rut_empleado = models.IntegerField()
    dv = models.CharField(max_length=1)
    celular = models.IntegerField(null=True)
    nacimiento = models.DateField()
    nacionalidad = models.CharField(max_length=50, null=True)
    comuna = models.ForeignKey(Comuna, on_delete=models.PROTECT, null=True)
    direccion = models.CharField(max_length=200, null=True)
    numero_direccion = models.CharField(max_length=20, null=True)
    pedidos = models.BooleanField(help_text="¿Puede realizar pedidos?")


class TipoCliente(models.Model):
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.descripcion

class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    estatus = models.BooleanField(default=True)
    razon_social = models.CharField(max_length=100)
    rut_empresa = models.IntegerField()
    dv = models.CharField(max_length=1)
    direccion = models.CharField(max_length=100, null=True)
    comuna = models.ForeignKey(Comuna, on_delete=models.PROTECT, null=True)
    celular = models.IntegerField(null=True)
    nombre_comercial = models.CharField(max_length=100, null=True)
    tipo_cliente = models.ForeignKey(TipoCliente, on_delete=models.PROTECT, default=0)
    codigo = models.IntegerField(null=True)

class EstadoHabitacion(models.Model):
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.descripcion

class TipoHabitacion(models.Model):
    descripcion = models.CharField(max_length=50)
    estado = models.BooleanField(default=True)
    capacidad = models.IntegerField(default=0)

    def __str__(self):
        return self.descripcion

class Habitacion(models.Model):
    numero_habitacion = models.IntegerField()
    precio = models.IntegerField()
    descripcion = models.CharField(max_length=200)
    estado_habitacion = models.ForeignKey(EstadoHabitacion, on_delete=models.PROTECT, default=0)
    tipo_habitacion = models.ForeignKey(TipoHabitacion, on_delete=models.PROTECT, default=0)
    imagen = models.CharField(max_length=100, null=True)
    estado = models.BooleanField(default=True)
    muestra_menu = models.BooleanField(default=True)

    def __str__(self):
        return str(self.numero_habitacion)



class Accesorio(models.Model):
    descripcion = models.CharField(max_length=20)
    estatus = models.BooleanField(default=True)

    def __str__(self):
        return self.descripcion

class HabitacionAccesorio(models.Model):
    tipo_habitacion = models.ForeignKey(TipoHabitacion, on_delete=models.PROTECT, default=0)
    accesorio = models.ForeignKey(Accesorio, on_delete=models.PROTECT, default=0)

class ServicioAdicional(models.Model):
    nombre = models.CharField(max_length=50, default="")
    descripcion = models.CharField(max_length=50)
    precio = models.IntegerField()
    mostrar_inicio = models.BooleanField(default=False)
    imagen = models.CharField(max_length=100, null=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.descripcion

class DetalleServicioAdicional(models.Model):
    detalle_orden_compra = models.ForeignKey("DetalleOrdenCompra", on_delete=models.PROTECT, default=0, null=True)
    servicio_adicional = models.ForeignKey("ServicioAdicional", on_delete=models.PROTECT, default=0)

class EstatusOrdenCompra(models.Model):
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.descripcion

class TipoComedor(models.Model):
    descripcion = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)
    precio = models.IntegerField(default=0)

    def __str__(self):
        return self.descripcion

class PlatoSemanal(models.Model):
    tipo_comedor = models.ForeignKey(TipoComedor, on_delete=models.PROTECT, default=0)
    descripcion = models.CharField(max_length=100)
    dia_desde = models.DateField()
    dia_hasta = models.DateField()
    imagen = models.CharField(max_length=100, null=True)
    estado = models.BooleanField(default=True)

class OrdenCompra(models.Model):
    fecha_emision = models.DateField(auto_now_add=True)
    monto_neto = models.IntegerField(null=True)
    iva = models.IntegerField(null=True)
    monto_total = models.IntegerField(null=True)
    cantidad_huesped = models.IntegerField()
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, default=0)
    estatus_orden_compra = models.ForeignKey(EstatusOrdenCompra, on_delete=models.PROTECT, default=0)

class DetalleOrdenCompra(models.Model):
    orden_compra = models.ForeignKey(OrdenCompra, on_delete=models.PROTECT, default=0)
    inicio_estadia = models.DateField()
    final_estadia = models.DateField()
    monto = models.IntegerField(null=True)

class Huesped(models.Model):
    rut = models.IntegerField()
    dv = models.CharField(max_length=1)
    nombre = models.CharField(max_length=30)
    apellido_p = models.CharField(max_length=50)
    apellido_m = models.CharField(max_length=50)
    email = models.CharField(max_length=50, null=True)
    telefono = models.IntegerField(null=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, default=0)
    fecha_nac = models.DateField(null=True)
    estado = models.BooleanField(default=True)

class HuespedDetalle(models.Model):
    detalle_orden_compra = models.ForeignKey(DetalleOrdenCompra, on_delete=models.PROTECT, default=0)
    rut_huesped = models.ForeignKey(Huesped, on_delete=models.PROTECT, default=0)
    check_in = models.BooleanField(default=False)

class Reserva(models.Model):
    detalle_orden_compra = models.ForeignKey(DetalleOrdenCompra, on_delete=models.PROTECT, default=0)
    huesped = models.ForeignKey(Huesped, on_delete=models.PROTECT, default=0)
    check_in = models.BooleanField(null=True)
    habitacion = models.ForeignKey(Habitacion, on_delete=models.PROTECT, default=0)
    plato = models.IntegerField(null=True)
    tipo_comedor = models.ForeignKey(TipoComedor, on_delete=models.PROTECT, default=0)

class Categoria(models.Model):
    descripcion = models.CharField(max_length=100)
    estatus = models.BooleanField(default=True)

    def __str__(self):
        return self.descripcion

class TipoProducto(models.Model):
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.descripcion

class Producto(models.Model):
    especificacion = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)
    precio = models.IntegerField()
    stock = models.IntegerField()
    stock_critico = models.IntegerField()
    fecha_vencimiento = models.DateField(null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, default=0)
    tipo_producto = models.ForeignKey(TipoProducto, on_delete=models.PROTECT, default=0)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.descripcion

class EstatusOrdenPedido(models.Model):
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.descripcion

class OrdenPedido(models.Model):
    fecha_emision = models.DateField(auto_now_add=True)
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT, default=0)
    estatus_orden_pedido = models.ForeignKey(EstatusOrdenPedido, on_delete=models.PROTECT, default=0)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, default=0)
    observacion = models.CharField(max_length=500, null=True)

class DetalleOrdenPedido(models.Model):
    cantidad = models.IntegerField()
    orden_pedido = models.ForeignKey(OrdenPedido, on_delete=models.PROTECT, default=0)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, default=0)

class EstatusRecepcion(models.Model):
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.descripcion

class RecepcionOrdenPedido(models.Model):
    fecha_entrega = models.DateField()
    id_detalle_pedido = models.IntegerField()
    estatus_recepcion = models.ForeignKey(EstatusRecepcion, on_delete=models.PROTECT, default=0)
    observacion = models.CharField(max_length=500, null=True)

class EstatusDocumento(models.Model):#Modifiqué
    descripcion = models.CharField(max_length=50)
    def __str__(self):
        return self.descripcion
class TipoDocumento(models.Model):#Modifiqué
    codigo_sii = models.CharField(max_length=2, primary_key=True)
    descripcion = models.CharField(max_length=40,default='')
    abreviado = models.CharField(max_length=3,default='')
    estado = models.BooleanField(default=True)

class Documento(models.Model):#Modifiqué
   tipo_doc = models.ForeignKey(TipoDocumento, on_delete=models.PROTECT)
   nro_ocompra = models.ForeignKey(OrdenCompra, on_delete=models.PROTECT, null=True)
   nro_opedido = models.ForeignKey(OrdenPedido, on_delete=models.PROTECT, null=True)
   iva = models.IntegerField()
   fecha_emision = models.DateField(auto_now_add=True)
   monto_neto = models.IntegerField(blank=True)
   iva = models.IntegerField()
   monto_total = models.IntegerField()
   estado_documento = models.ForeignKey(EstatusDocumento, on_delete=models.PROTECT, default=0)