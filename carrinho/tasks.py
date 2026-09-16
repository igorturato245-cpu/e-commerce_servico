from celery import shared_task
from .models import Carrinho
from django.utils.timezone import now
from datetime import timedelta
from abc import ABC, abstractmethod

class AbstractLimpezaCarrinho(ABC):
    
    @abstractmethod
    def executa_limpeza_carrinho(self):
        pass
    
    
class ConcretLimpezaCarrinho(AbstractLimpezaCarrinho):
    
    def executa_limpeza_carrinho(self):
        
        limite=now()-timedelta(days=7)
        
        limite_logado=now()-timedelta(days=30)
        
        
        deletados,_=Carrinho.objects.filter(
            criado_em__lt=limite,
            usuario__isnull=True,
            itens__isnull=True
        ).delete()
        
        
        deletados_logados,_=Carrinho.objects.filter(
            criado_em__lt=limite_logado,
            usuario__isnull=False
        ).filter(pedido__isnull=True).delete()
        
        return f'Limpeza concluída:{deletados} anônimos e {deletados_logados} logados removidos.'
    
@shared_task(name="task_limpar_carrinhos")
def task_limpar_carrinho():
    obj=ConcretLimpezaCarrinho
    return obj.executa_limpeza_carrinho