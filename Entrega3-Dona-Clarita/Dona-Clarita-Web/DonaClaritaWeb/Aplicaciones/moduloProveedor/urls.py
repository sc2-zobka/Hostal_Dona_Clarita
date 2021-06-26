from django.urls import path
from Aplicaciones.moduloProveedor.views import  ordenes_proveedor, rechaza_ordenPedido, acepta_ordenPedido
                  

urlpatterns = [
#***Módulo:Empleados*** Opción: inicio
    #path('dashboard/', dashboard, name="dashboard"),
    #***Módulo:Empleados*** Opción: clientes
    path('dashboard/listado-pedidos/', ordenes_proveedor, name="ordenes-proveedor"),
    path('dashboard/rechaza-proveedor/<id>/', rechaza_ordenPedido, name="rechaza-proveedor"),
    path('dashboard/acepta-proveedor/<id>/', acepta_ordenPedido, name="acepta-proveedor"),


]