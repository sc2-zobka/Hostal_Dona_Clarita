from django.urls import path
from Aplicaciones.moduloEmpleado.views import  dashboard,\
                   clientes, documentos, edit_clientes, eliminar_cliente,cliente_pass, nuevo_proveedor, proveedores, edit_proveedor, eliminar_proveedor, proveedor_pass, \
                   empleados, edit_empleado,nuevo_empleado, eliminar_empleado, empleado_pass, tipo_empleado, editar_tipoEmpleado, eliminar_tipoEmpleado, \
                   nueva_habitacion, edit_habitacion, elim_habitacion, habitaciones, tipo_habitacion, edit_tipo_hab, elim_tipo_hab, accesorios, edit_accesorios, eliminar_accesorios,\
                   nuevo_plato, edit_plato, platos, tipo_comedor, edit_tipo_comedor, eliminar_tipo_comedor, eliminar_platos,\
                   nuevo_servicio_ad, servicios_ad, edit_servicioad, eliminar_servicioad,\
                   huespedes, nuevo_huesped, huesped_carga,edit_huesped, eliminar_huesped, \
                   productos, nuevo_producto,edit_producto, eliminar_producto, tipo_producto, edit_tipo_producto, eliminar_tipo_producto,  categoria, edit_categoria, eliminar_categoria,\
                   nueva_ordenPedido, ordenes_pedido, edit_ordenPedido, check_ordenPedido, anular_ordenPedido, rechazar_ordenPedido,print_pedidos,\
                   comentarios,  documentos, orden_compra_views, facturarOC, notaCredito, reservas, check_in



urlpatterns = [
#***Módulo:Empleados*** Opción: inicio
    path('dashboard/', dashboard, name="dashboard"),
    #***Módulo:Empleados*** Opción: clientes
    path('dashboard/clientes/', clientes, name="clientes-list"),
    path('dashboard/edit-cliente/<id>/', edit_clientes, name="edit-cliente"),
    path('dashboard/eliminar_cliente/<id>/', eliminar_cliente, name="eliminar-cliente"),
    path('dashboard/pass-cliente/<id>/', cliente_pass, name="pass-cliente"),

     #***Módulo:Empleados*** Opción: empleados
    path('dashboard/empleados/', empleados, name="empleados-list"),
    path('dashboard/nuevo-empleado/', nuevo_empleado, name="empleado-new"),
    path('dashboard/edit-empleado/<id>/', edit_empleado, name="edit-empleado"),
    path('dashboard/pass-empleado/<id>/', empleado_pass, name="pass-empleado"),
    path('dashboard/eliminar-empleado/<id>/', eliminar_empleado, name="eliminar-empleado"),
    path('dashboard/tipo-empleado/', tipo_empleado, name="tipo-empleado"),
    path('dashboard/edit-tipo-empleado/<id>/', editar_tipoEmpleado, name="edit-tipo-empleado"),
    path('dashboard/elim-tipo-empleado/<id>/', eliminar_tipoEmpleado, name="elim-tipo-empleado"),
     #***Módulo:Empleados*** Opción: proveedores
    path('dashboard/nuevo-proveedor/', nuevo_proveedor, name="proveedor-new"),
    path('dashboard/edit-proveedor/<id>/', edit_proveedor, name="edit-proveedor"),
    path('dashboard/eliminar-proveedor/<id>/', eliminar_proveedor, name="eliminar-proveedor"),
    path('dashboard/proveedores/', proveedores, name="proveedores-list"),
    path('dashboard/pass-proveedor/<id>/', proveedor_pass, name="pass-proveedor"),
    #***Módulo:Empleados*** Opción: huéspedes
    path('dashboard/huespedes/', huespedes, name="huespedes-list"),
    path('dashboard/nuevo-huesped/', nuevo_huesped, name="huesped-new"),
    path('dashboard/edit-huesped/<id>/', edit_huesped, name="edit-huesped"),    
    path('dashboard/eliminar-huesped/<id>/', eliminar_huesped, name="eliminar-huesped"),    
    path('dashboard/carga-huespedes/', huesped_carga, name="huesped-carga"), 
    #***Módulo:Empleados*** Opción: servicios habitación
    path('dashboard/nueva-habitacion/', nueva_habitacion, name="habitacion-new"),
    path('dashboard/edit-habitacion/<id>/', edit_habitacion, name="edit-habitacion"),
    path('dashboard/elim-habitacion/<id>/', elim_habitacion, name="elim-habitacion"),
    path('dashboard/habitaciones/', habitaciones, name="habitaciones-list"),
    path('dashboard/tipo-habitacion/', tipo_habitacion, name="tipo-habitacion"),
    path('dashboard/edit-tipo-habitacion/<id>/', edit_tipo_hab, name="edit-tipo-habitacion"),
    path('dashboard/elim-tipo-habitacion/<id>/', elim_tipo_hab, name="elim-tipo-habitacion"),
    path('dashboard/accesorios/', accesorios, name="accesorios-new"),
    path('dashboard/edit-accesorio/<id>/', edit_accesorios, name="edit-accesorio"),
    path('dashboard/eliminar-accesorio/<id>/', eliminar_accesorios, name="eliminar-accesorio"),
    #***Módulo:Empleados*** Opción: servicios comedor
    path('dashboard/nuevo-plato/', nuevo_plato, name="plato-new"),  
    path('dashboard/platos/', platos, name="platos-list"),
    path('dashboard/edit-plato/<id>/', edit_plato, name="edit-plato"),
    path('dashboard/eliminar-plato/<id>/', eliminar_platos, name="eliminar-plato"),
    path('dashboard/tipo-comedor/', tipo_comedor, name="tipo-comedor"),
    path('dashboard/edit-tipo-comedor/<id>/', edit_tipo_comedor, name="edit-tipo-comedor"),
    path('dashboard/elim-tipo-comedor/<id>/', eliminar_tipo_comedor, name="elim-tipo-comedor"),
    
    #***Módulo:Empleados*** Opción: servicios adicionales
    path('dashboard/nuevo-servicio/', nuevo_servicio_ad, name="servicio-new"),
    path('dashboard/servicios/', servicios_ad, name="servicios-list"),
    path('dashboard/edit-servicio/<id>/', edit_servicioad, name="edit-servicio"),
    path('dashboard/eliminar-servicio/<id>/', eliminar_servicioad, name="eliminar-servicio"),


     #***Módulo:Empleados*** Opción: Productos
    path('dashboard/nuevo-producto/', nuevo_producto, name="producto-new"),
    path('dashboard/edit-producto/<id>/', edit_producto, name="producto-edit"),
    path('dashboard/productos/', productos, name="productos-list"),
    path('dashboard/eliminar-producto/<id>/', eliminar_producto, name="eliminar-producto"),


    #***Módulo:Empleados*** Opción: Productos - Tipo Producto
    path('dashboard/tipo-producto/', tipo_producto, name="tipo-producto"),
    path('dashboard/edit-tipo-producto/<id>/', edit_tipo_producto, name="edit-tipo-producto"),
    path('dashboard/eliminar-tipo-producto/<id>/', eliminar_tipo_producto, name="eliminar-tipo-producto"),

     #***Módulo:Empleados*** Opción: Productos - Categoria
    path('dashboard/nueva-categoria/', categoria, name="categoria-new"),
    path('dashboard/eliminar-categoria/<id>/', eliminar_categoria, name="eliminar-categoria"),
    path('dashboard/edit-categoria//<id>/', edit_categoria, name="edit-categoria"),

    #***Módulo:Empleados*** Opción: ordenes pedidos
    path('dashboard/nueva-orden-pedido/', nueva_ordenPedido, name="orden-pedido-new"),
    path('dashboard/ordenes-pedidos/', ordenes_pedido, name="ordenes-pedidos-list"),
    path('dashboard/edit-orden-pedido/<id>/', edit_ordenPedido, name="edit-orden-pedido"),
    path('dashboard/check-orden-pedido/<id>/', check_ordenPedido, name="check-orden-pedido"),
    path('dashboard/anular-orden-pedido/<id>/', anular_ordenPedido, name="anular-orden-pedido"),
    path('dashboard/rechazar-orden-pedido/<id>/', rechazar_ordenPedido, name="rechazar-orden-pedido"),
    path('dashboard/orden-pedido/<id>/', print_pedidos, name="print-pedidos"),

    # path('dashboard/recepcionar-orden-pedido/<id>/<obs>/', recepcionar_ordenPedido, name="recepcionar-orden-pedido"),




    path('dashboard/comentarios/', comentarios, name="comentarios"),
    path('dashboard/documentos-tributarios/', documentos, name="ventas"),
    path('dashboard/ordenes-compras/', orden_compra_views, name="oc-list-views"),
    path('dashboard/facturar-oc/<id>/', facturarOC, name="facturar-oc"),
    path('dashboard/notacredito/<id>/', notaCredito, name="notacredito"),
    path('dashboard/reservas/', reservas, name="reservas"),
    path('dashboard/check-in/<id>/', check_in, name="check-in"),


]