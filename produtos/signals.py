from django.db.models.signals import post_save
from django.dispatch import receiver
from utils.atualiza_estoque import AtualizaEstoque
from pagamentos.models import Pedido


@receiver(post_save,sender=Pedido)
def atualizar_pedido_pago(sender,instance,*args, **kwargs):
    if instance.status=='paid' and not instance.estoque_baixado:
        obj=AtualizaEstoque()
        obj.atualiza_estoque(instance.id)
            
@receiver(post_save,sender=Pedido)
def atualiza_estoque_devolvido(sender,instance,*args, **kwargs):
    if instance.status=='cancelled' and instance.estoque_baixado:
        obj=AtualizaEstoque()
        obj.atualiza_estoque_cancelado(instance.id)