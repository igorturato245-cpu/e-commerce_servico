import json
import logging
from django.views import View
from produtos.models import Product
from pagamentos.models import Pedido
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from integrations.dropify.dropify_gateways import DropifyStrategy

logger=logging.getLogger(__name__)

@method_decorator(csrf_exempt,name='dispatch')
class DropifyWebhooks(View):
    def post(self,request):
        
        data=json.loads(request.body)
        
        evento=data.get('event')
        
        gateway=DropifyStrategy()
        
        try:
            if evento == 'stock':            
                erp_id=data.get('product')
            
                if erp_id:
                    novo_estoque=gateway.checar_estoque(erp_id)
                    Product.objects.filter(erp_id=erp_id).update(
                        estoque=novo_estoque,
                        remote_stock=novo_estoque
                    )
                
            elif evento == 'price':          
                erp_id=data.get('product')
            
                if erp_id:
                    novo_preco=gateway.preco_atual_produto(erp_id)
                    Product.objects.filter(erp_id=erp_id).update(
                        preco=novo_preco,
                    )
                
            elif evento == 'order-status':           
                order_id=data.get('orderId')
            
                if order_id:
                    novo_status,codigo_rastreio=gateway.status_pedido(order_id)
                    Pedido.objects.filter(erp_order_id=order_id).update(
                        status=novo_status,
                        erp_status=novo_status,
                        tracking_code=codigo_rastreio
                    )
        
        except Exception as e:
            logger.error(f'Erro no webhook da dropify:{e}')
        return HttpResponse('OK',status=200)
        