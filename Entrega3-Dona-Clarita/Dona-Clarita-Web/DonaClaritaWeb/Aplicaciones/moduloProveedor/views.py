from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
# Create your views here.
def ordenes_proveedor(request):
    ordenes_pedido_db = ''
    with connection.cursor() as cursor:
        try:
            if request.user.is_proveedor:
                idProveedor =request.user.id
                cursor.execute(f"SELECT RUT_EMPRESA FROM CLIENTE WHERE ID_USUARIO = {idProveedor}")
                rutProveedor = cursor.fetchone()[0]
                cursor.execute(f"""SELECT OP.ID_ORDEN_PEDIDO, CL.RAZON_SOCIAL, OP.FECHA_EMISION, ROP.FECHA_ENTREGA,
                    SUM(DOP.CANTIDAD), EOP.DESCRIPCION, ROP.OBSERVACION
                    FROM ORDEN_PEDIDO OP
                    JOIN DETALLE_ORDEN_PEDIDO DOP ON OP.ID_ORDEN_PEDIDO = DOP.ID_ORDEN_PEDIDO
                    JOIN ESTATUS_ORDEN_PEDIDO EOP ON OP.ID_ESTATUS_ORDEN_PEDIDO = EOP.ID_ESTATUS_ORDEN_PEDIDO 
                    LEFT JOIN RECEPCION_ORDEN_PEDIDO ROP ON DOP.ID_ORDEN_PEDIDO = ROP.ID_ORDEN_PEDIDO 
                    JOIN CLIENTE CL ON OP.ID_CLIENTE = CL.ID_CLIENTE
                    WHERE CL.RUT_EMPRESA = {rutProveedor}
                    GROUP BY OP.ID_ORDEN_PEDIDO, CL.RAZON_SOCIAL, OP.FECHA_EMISION, ROP.FECHA_ENTREGA, 
                    EOP.DESCRIPCION, ROP.OBSERVACION """)
                ordenes_pedido_db = cursor.fetchall()
            
        except Exception as e:
            print(e)
            pass

    data = {
        "pedidos": ordenes_pedido_db
    }    
    return render(request, 'Proveedor/ordenes_pedido.html',data)

def acepta_ordenPedido(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT ID_ESTATUS_ORDEN_PEDIDO FROM ESTATUS_ORDEN_PEDIDO " \
                "WHERE DESCRIPCION LIKE %s", ['PENDIENTE RECEPCION'])
            estatus_db = cursor.fetchone()

            cursor.execute("UPDATE ORDEN_PEDIDO SET ID_ESTATUS_ORDEN_PEDIDO = %s " \
                "WHERE ID_ORDEN_PEDIDO = %s", [estatus_db[0], id])

            messages.success(request, f'Orden de pedido #{id} rechazada correctamente')
            return redirect('ordenes-proveedor')
        except Exception as e:
            messages.error(request, 'Orden de pedido no se pudo modificar')
            print(e)

    return redirect('ordenes-proveedor')

def rechaza_ordenPedido(request, id):
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT ID_ESTATUS_ORDEN_PEDIDO FROM ESTATUS_ORDEN_PEDIDO " \
                "WHERE DESCRIPCION LIKE %s", ['RECHAZA PROVEEDOR'])
            estatus_db = cursor.fetchone()

            cursor.execute("UPDATE ORDEN_PEDIDO SET ID_ESTATUS_ORDEN_PEDIDO = %s " \
                "WHERE ID_ORDEN_PEDIDO = %s", [estatus_db[0], id])

            messages.success(request, f'Orden de pedido #{id} rechazada correctamente')
            return redirect('ordenes-proveedor')
        except Exception as e:
            messages.error(request, 'Orden de pedido no se pudo modificar')
            print(e)

    return redirect('ordenes-proveedor')