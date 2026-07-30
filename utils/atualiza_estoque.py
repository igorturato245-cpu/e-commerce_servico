import logging
from django.db import transaction
from pagamentos.models import Pedido

logger=logging.getLogger(__name__)

class AtualizaEstoque:
    def atualiza_estoque(self,pedido_id):
        with transaction.atomic():
            pedido=Pedido.objects.select_for_update().get(id=pedido_id)
            
            if pedido.estoque_baixado:
                return
            
            
            items=pedido.itens_pedido.select_related('produto').all()#type:ignore
            
            
            for item in items:
                
                try:
                    if item.produto:
                        item.produto.atualiza_estoque_paid(item.quantidade)
                        
                    else:
                        logger.error(f'Não foi possível atualizar o estoque.')
                        
                except Exception as e:
                    logger.error(f'Erro no item {pedido}:{e}')
                    
                    
            pedido.estoque_baixado=True
            pedido.save(update_fields=['estoque_baixado'])
            
    def atualiza_estoque_cancelado(self,pedido_id):
        with transaction.atomic():
            pedido=Pedido.objects.select_for_update().get(id=pedido_id)
            
            if not pedido.estoque_baixado:
                return
            
            
            items=pedido.itens_pedido.select_related('produto').all()#type:ignore
            
            
            for item in items:
                try:
                    
                    if item.produto:
                        item.produto.atualiza_estoque_devolvido(item.quantidade)
                        
                    else:
                        logger.error(f'Não foi possível atualizar o estoque.')
                        
                except Exception as e:
                    logger.error(f'Erro no item {pedido}:{e}')
                    
            pedido.estoque_baixado=False
            pedido.save(update_fields=['estoque_baixado'])