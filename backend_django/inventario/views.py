from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import uuid

# Importamos del archivo que configuramos anteriormente
from transbank.webpay.webpay_plus.transaction import Transaction
from .models import Producto, Pedido
from .serializers import ProductoSerializer, PedidoSerializer

# 1. API estándar para que React liste y vea detalles de Productos
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [AllowAny]

# 2. Endpoint para iniciar el pago en Webpay Plus
@api_view(['POST'])
@permission_classes([AllowAny])
def iniciar_pago_webpay(request):
    """Recibe el monto desde React, crea el Pedido e inicializa Webpay."""
    monto = request.data.get("monto")
    if not monto:
        return Response({"error": "El monto es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Generar un número de orden único para Transbank
    orden_numero = f"MED-{uuid.uuid4().hex[:8].upper()}"
    
    # Crear el registro del pedido como PENDIENTE en tu Base de Datos
    pedido = Pedido.objects.create(
        orden_numero=orden_numero,
        monto_total=int(monto),
        estado_pago='PENDIENTE'
    )
    
    # URL a donde Webpay redirigirá al usuario tras poner su tarjeta
    # NOTA: En producción, apunta esto a tu dominio o IP pública
    return_url = "http://localhost:8000/api/webpay-callback/"
    
    try:
        tx = Transaction() # Carga ambiente de Sandbox automático
        response = tx.create(
            buy_order=orden_numero,
            session_id="session_medistock",
            amount=int(monto),
            return_url=return_url
        )
        
        # Guardar el token de Transbank temporalmente en el pedido
        pedido.token_webpay = response['token']
        pedido.save()
        
        # Retornamos el token y la URL de Webpay hacia el Frontend
        return Response({
            "token": response['token'],
            "url": response['url'],
            "orden_numero": orden_numero
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": f"Error Transbank: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 3. Endpoint Callback donde Transbank devuelve al cliente
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def webpay_callback(request):
    """Captura el token que envía Transbank, confirma el pago y actualiza el pedido."""
    # Transbank puede enviar el token por POST o GET dependiendo de la etapa
    token = request.data.get("token_ws") or request.query_params.get("token_ws")
    
    if not token:
        return Response({"error": "Token no recibido"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        tx = Transaction()
        # El método commit confirma la transacción obligatoriamente (Captura de fondos)
        result = tx.commit(token=token)
        
        # Buscamos el pedido asociado a ese token en nuestra BD
        pedido = Pedido.objects.get(token_webpay=token)
        
        if result.get("vci") == "TSY" and result.get("status") == "AUTHORIZED":
            pedido.estado_pago = 'PAGADO'
            pedido.save()
            # Redirigir al éxito en el Frontend de React
            return Response({"status": "Aprobado", "orden": pedido.orden_numero}, status=status.HTTP_200_OK)
        else:
            pedido.estado_pago = 'RECHAZADO'
            pedido.save()
            return Response({"status": "Rechazado o Cancelado"}, status=status.HTTP_200_OK)
            
    except Pedido.DoesNotExist:
        return Response({"error": "Pedido no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Error en confirmación: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)