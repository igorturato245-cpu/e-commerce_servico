from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .models import Pedido,Solicitacao_reembolso
from utils.email_para_o_usuario import EmailForUser


    
@receiver(pre_save,sender=Pedido)
def capturar_status_anterior(sender,instance,**kwargs):
    if instance.pk:
        try:
            old_instance=Pedido.objects.get(id=instance.pk)
            instance._old_status=old_instance.status
            instance._old_erp_status=old_instance.erp_status
        except Pedido.DoesNotExist:
            instance._old_status=None
            instance._old_erp_status=None
                
    else:
        instance._old_status=None
        instance._old_erp_status=None
            
@receiver(post_save,sender=Pedido)
def disparar_email_cancelamento_direto(sender,instance,created, **kwargs):
    if instance.status=='cancelled' and getattr(instance,'_old_status',None) != 'cancelled':
        obj=EmailForUser()
        obj.enviar_email_cancelamento_direto(instance)
            
@receiver(post_save,sender=Solicitacao_reembolso)
def disparar_email_apos_mudanca_reembolso(sender,instance,created,**kwargs):
    obj=EmailForUser()
    obj.enviar_email_status_reembolso(instance,instance.pedido)
        
    
@receiver(post_save,sender=Pedido)
def apagar_carrinho_pago(sender,instance,created,**kwargs):
    if instance.status=='paid':
        if getattr(instance,'carrinho_id',None):
            instance.delete_cart_paid()
                
@receiver(post_save,sender=Solicitacao_reembolso)
def alterar_status_pedido_apos_solicitacao(sender,instance,created,**kwargs):
    if created:
        pedido=instance.pedido
        pedido.status='cancelled'
        pedido.save(update_fields=['status'])