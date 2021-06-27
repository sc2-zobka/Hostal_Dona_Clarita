from django.contrib import admin
from .models import *

    

# Register your models here.
admin.site.register(User)
admin.site.register(Configuracion)
admin.site.register(TipoMoneda)
admin.site.register(TipoEmpleado)
admin.site.register(Pais)
admin.site.register(Region)
admin.site.register(Comuna)
admin.site.register(Empleado)
admin.site.register(TipoCliente)
admin.site.register(Cliente)
admin.site.register(EstadoHabitacion)
admin.site.register(TipoHabitacion)
admin.site.register(Habitacion)
admin.site.register(EstatusDocumento)
admin.site.register(Documento)
admin.site.register(TipoDocumento)
admin.site.register(Accesorio)
admin.site.register(HabitacionAccesorio)
admin.site.register(ServicioAdicional)
admin.site.register(EstatusOrdenCompra)
admin.site.register(TipoComedor)
admin.site.register(PlatoSemanal)
admin.site.register(OrdenCompra)
admin.site.register(DetalleOrdenCompra)
admin.site.register(Huesped)
admin.site.register(Categoria)
admin.site.register(TipoProducto)
admin.site.register(Producto)
admin.site.register(EstatusOrdenPedido)
admin.site.register(OrdenPedido)
admin.site.register(DetalleOrdenPedido)
admin.site.register(EstatusRecepcion)
admin.site.register(RecepcionOrdenPedido)
