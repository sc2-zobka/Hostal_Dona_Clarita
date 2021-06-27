from django.urls import path
from Aplicaciones.moduloCliente.views import *
from Aplicaciones.moduloEmpleado.views import huespedes, nuevo_huesped, edit_huesped, huesped_carga

urlpatterns = [
     #***Módulo:Empleados*** Opción: empleados
    path('dashboard/Inicio/', dashboard_cli, name="dashboard-cli"),
    path('dashboard/trabajadores/', huespedes, name="trabajadores-list"),
    path('dashboard/nuevo-trabajador/', nuevo_huesped, name="trabajador-new"), 
    path('dashboard/edit-trabajador/<id>/', edit_huesped, name="edit-trabajador"),   
    path('dashboard/carga-trabajadores/', huesped_carga, name="trabajadores-carga"),    
    path('dashboard/ordenes-compra/', ordenes_compras, name="oc-list"),
    path('dashboard/nueva-orden-compra/', nueva_orden_compra, name="oc-new"),  
    path('dashboard/mis-documentos/', facturas_cli, name="facturas-cli"),  
    path('dashboard/documento/<id>/', factura_print, name="factura-print"),
    path('dashboard/orden-compra/<id>/', print_orden_compra, name="oc-print"),
    path('dashboard/opinion/<id>/', nueva_opinion, name="opinion")

]