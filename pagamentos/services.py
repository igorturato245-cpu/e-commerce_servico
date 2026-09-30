import logging
from pagamentos.models import Pedido,Pedidoitem
from cadastro_de_usuarios.models import Endereco_usuario
from django.db import transaction
from django.shortcuts import render,redirect,get_object_or_404
from abc import ABC,abstractmethod
from django.contrib import messages
from django.urls import reverse
from pagamentos.gateweys.gatewyes import PagseguroStrategy as pagseguro_integration
from integrations.dropify.dropify_gateways import DropifyStrategy
from utils.google_sheets import GoogleSheets
from utils.email_para_o_usuario import EmailForUser
      
logger=logging.getLogger(__name__)

class CheckoutService:
    
    def processar_novo_pedido(self,request,carrinho,user):
        if Pedido.objects.filter(usuario=user,carrinho=carrinho).exists():
            raise ValueError('Esse pedido já existe.Vá em "Meus Pedidos" para tentar pagar novamente.')
        
        endereco=get_object_or_404(Endereco_usuario,usuario=request.user,padrao=True)
        
        if not endereco:
            raise ValueError('Nenhum endereço padrão encontrado.')

        items=carrinho.itens.select_related('produto').all()
        
        total=carrinho.total()          
               
        
        itens_para_calculo=[]
        for item in items:
            itens_para_calculo.append({
                'id':item.produto.erp_id or str(item.produto.id),
                'quantity':item.quantidade
            })
        
        
        total_com_frete=Pedido.calcula_total(endereco.cep,itens_para_calculo,total)
        
        
        
        try:
            with transaction.atomic():
                pedido=Pedido.objects.create(
                    usuario=request.user,
                    carrinho=carrinho,
                    total=total_com_frete['total_produtos'],
                    valor_frete=total_com_frete['valor_frete'],
                    total_com_frete=total_com_frete['total_com_frete'],
                    status='pending',
                    erp_status='pending'
                )
                for it in items:
                    Pedidoitem.objects.create(
                        pedido=pedido,
                        produto=it.produto,
                        produto_id_str=str(it.produto.erp_id or it.produto.id),
                        produto_name=it.produto.name,
                        quantidade=it.quantidade,
                        price=it.produto.get_preco()
                    )
    
        except Exception:
            raise ValueError('Pedido já está sendo processado, aguarde alguns instantes.')
        
        gateway=PagseguroGateway()
        url_redirect=gateway.gerar_pagamento(request,endereco,pedido)
        
        return url_redirect
        
    @classmethod 
    def processar_retry(cls, request, pedido, user):
        endereco=Endereco_usuario.objects.filter(usuario=user,padrao=True).first()
        
        if not endereco:
            raise ValueError('Nenhum endereço padrão encontrado para o retry.')
        
        gateway=PagseguroGateway()
        url_redirect=gateway.gerar_pagamento(request,endereco,pedido)
        
        return url_redirect
    
    @classmethod
    def cancelar_pedido(cls,pedido)->bool:
        with transaction.atomic():
            
            servico=PagseguroGateway()
            servico.cancelar_pedido(pedido)
            
            pedido.status='cancelled'
            pedido.save()
                                
            #send_order_cancelled_to_erp_task.dalay(pedido.id)
            
        return True
    
    @classmethod
    def solicitacao_reembolso(cls,pedido,status_solicitacao)->bool:
        with transaction.atomic():
            
            servico=PagseguroGateway()
            servico.solicitacao_reembolso(pedido)
            
            pedido.status='refunded'
            pedido.erp_status='return'
            pedido.save(update_fields=['status','erp_status'])
            
            status_solicitacao.status='completed'
            status_solicitacao.save(update_fields=['status'])
            
        return True
            
            
    def atualiza_status_notificacao(self,order_id):
        send_to=PagseguroGateway()
        data=send_to.processar_notificacao(order_id)
            
        ref=data.get('reference')
        status_str=data.get('status')
            
            
        with transaction.atomic():
            pedido=Pedido.objects.select_related().filter(payment_reference=ref).first()
                
                
            if not pedido:
                raise ValueError(f'Pedido com referência {ref} não encontrado no banco.')
                
                
            status_map = {
                'WAITING': 'pending', 
                'IN_ANALYSIS': 'pending',
                'AUTHORIZED': 'paid', 
                'PAID': 'paid',    
                'CANCELED': 'cancelled', 
                'DECLINED': 'cancelled',
                'REFUNDED': 'refunded',
            }
                
            new_status=status_map.get(status_str,'pending')
                
                
            if pedido.status != new_status:
                pedido.status = new_status
                pedido.erp_status=new_status
                pedido.metadata=pedido.metadata or {}
                pedido.metadata.update({
                    'pagseguro_status':status_str,
                    'pagseguro_last_update':data.get('lastEventDate'),
                    'pagseguro_transaction_code':data.get('code'),
                    'pagseguro_charge_id':data.get('charge_id'),
                })
                pedido.save(update_fields=['status','erp_status','metadata'])
                
                try:
                    transaction.on_commit(lambda: GoogleSheets().enviar_pedido_sheets(pedido))
                    
                except Exception as e:
                    logger.error(f'Erro ao enviar pedido {pedido.pk} para o Google Sheets:{str(e)}')
                    
                try:
                    obj=EmailForUser()    
                    obj.enviar_email_status_pedido(pedido)
                    obj.enviar_email_status_erp_pedido(pedido)
                except Exception as e:
                    logger.error(f'Erro ao enviar e-mails do pedido {pedido.pk}:{str(e)} ')    
                    
        if new_status == 'paid' and not pedido.enviado_dropify:
            endereco=Endereco_usuario.objects.filter(usuario=pedido.usuario,padrao=True).first()
                    
            if not endereco:
                logger.critical(f'❌ Pedido #{pedido.pk} PAGO mas SEM ENDEREÇO para envio Dropify!')
                return
                    
            try:
                obj=DropifyStrategy()
                if obj.enviar_pedido(pedido,endereco):
                    pedido.enviado_dropify=True
                    pedido.erp_order_id=str(order_id)
                    pedido.save(update_fields=['enviado_dropify','erp_order_id'])
                    logger.info(f'✔ Pedido #{pedido.pk} enviado com sucesso para a Dropify!')                    
            except Exception as e:
                logger.error(f'❌ FALHA CRÍTICA ao enviar Pedido #{pedido.pk} para Dropify: {str(e)}')
            
            
            
            
            
            
        
    
    
class PaymentGatewayStrategy(ABC):
    
    @abstractmethod
    def gerar_pagamento(self,request,endereco,pedido)->str:
        pass
    
    @abstractmethod
    def cancelar_pedido(self, pedido)->str:
        pass
    
    @abstractmethod
    def solicitacao_reembolso(self,pedido)->str:
        pass
    
    @abstractmethod
    def processar_notificacao(self,order_id)->dict:
        pass


class PagseguroGateway(PaymentGatewayStrategy):    
    def gerar_pagamento(self, request, endereco, pedido):
        #try:
        return_url=request.build_absolute_uri(reverse('pagamentos:payment_return'))
        notification_url=request.build_absolute_uri(reverse('pagamentos:pagseguro_notify'))
            
            
        pg=pagseguro_integration()
            
        pg_data=pg.iniciar_pagamento(pedido,endereco,return_url,notification_url)
            
            
        pedido.payment_reference=pg_data['reference']
        pedido.metadata={'pagseguro':pg_data['code']}
        pedido.save(update_fields=['payment_reference','metadata'])
            
        #except Exception as e:
        #    raise ValueError('Erro ao processar pagamento. Tente novamente.')
        return pg_data['redirect_url']
    
    def cancelar_pedido(self, pedido) -> bool:
        if pedido.status=='paid':
                    
            charge_id=(pedido.metadata or {}).get('pagseguro_charge_id')
                    
            if not charge_id:
                raise Exception('Código de cobrança (Charge ID)')
                    
            pg=pagseguro_integration()
            
            pg_data=pg.reembolso_transacao(charge_id)
                    
            if not pg_data:
                raise Exception('Falha ao processar reembolso no PagSeguro.')

        
        return True
    
    def solicitacao_reembolso(self, pedido) -> bool:
        transaction_code=pedido.metadata.get('pagseguro')
        
        if not transaction_code:
            raise Exception('Código de transação do Pagseguro não encontrado no pedido.')
        
        pg=pagseguro_integration()
        
        pg_data=pg.reembolso_transacao(transaction_code)
        
        if not pg_data:
            raise ValueError('Falha ao processar reembolso no Pagseguro.')
        
        return True
    
    def processar_notificacao(self, order_id)->dict:
        pg=pagseguro_integration()
        data=pg.pega_notificacao(order_id)
        
        if not data or not pg.valida_notificacao(data):
            raise ValueError('Notificação inválida ou não encontrada no PagSeguro.')
            
            
        return data
