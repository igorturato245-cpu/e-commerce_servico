from django.shortcuts import redirect,get_object_or_404
from django.contrib import messages
from carrinho.views.view_carrinho import _get_card_for_request
from pagamentos.models import Pedido,Solicitacao_reembolso
from pagamentos.services import CheckoutService
from django.views import View
from pagamentos.models import Pedido
from django.http import HttpResponse
import json
import logging
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from utils.email_para_o_usuario import EmailForUser

logger=logging.getLogger(__name__)


class StartPaymentView(View):
    def post(self,request):
        if not request.user.is_authenticated:
            messages.error(request,'Usuario não esta logado, faça seu login para conseguir concluir sua compra.')
            return redirect('cadastro_login:login')
        
        
        cart=_get_card_for_request()
        carrinho=cart.get_carrinho(request)
        
        
        if not carrinho or not carrinho.itens.exists():#type:ignore
            messages.error(request,'Carrinho vazio.')
            return redirect('carrinho:carrinho_url')
    
        
        try:
            servico= CheckoutService()
            envio_de_dados=servico.processar_novo_pedido(request,carrinho,request.user)
            url_link=envio_de_dados
            
            pedido=get_object_or_404(Pedido,usuario=request.user,carrinho=carrinho)
            
            obj=EmailForUser()
            obj.enviar_email_pedido_recebido(pedido)
            
            return redirect(url_link)
        
        except ValueError as e:
            messages.error(request,str(e))
            messages.error(request,'Seu pedido já foi salvo, caso tenha tido problemas com o pagamento, cliquei em "detalhe" e tente o pagamento novamente.')
            return redirect('pagamentos:meus_pedidos')
            
        except Exception as e:
            messages.error(request,'Seu pedido já foi salvo, caso tenha tido problemas com o pagamento, cliquei em "detalhe" e tente o pagamento novamente.')
            return redirect('pagamentos:meus_pedidos')   

        
class RetryPaymentView(View):
    def post(self,request,pedido_id):
        if not request.user.is_authenticated:
            messages.error(request,'Usuario não está logado, faça seu login para conseguir concluir sua compra.')
            return redirect('cadastro_login:login')
        
        pedido=get_object_or_404(Pedido.objects.select_related(),pk=pedido_id,usuario=request.user)
        
        if pedido.status != 'pending':
            messages.error(request,'Erro ao processar pagamento.Status atual não permite retry.')
        

        try:
            servico=CheckoutService()
            envio_de_dados=servico.processar_retry(request,pedido, request.user)
            url_link=envio_de_dados
            
            return redirect(url_link)
        except ValueError as e:
            messages.error(request,str(e))
            return redirect('pagamentos:meus_pedidos')
        
        except Exception as e:
            messages.error(request,'Erro de comunicação com o gateway. Tente novamente.')
            return redirect('pagamentos:meus_pedidos')
        
class CancelledRefundedView(View):
    def post(self,request,pedido_id):
        
        pedido=get_object_or_404(Pedido,id=pedido_id,usuario=request.user)

        if pedido.pode_cancelar_direto:
            try:
                servico=CheckoutService()
                servico.cancelar_pedido(pedido)
                
                obj=EmailForUser()
                obj.enviar_email_cancelamento_direto(pedido.pk)
                
                return redirect('pagamentos:meus_pedidos')
                
            except ValueError as e:
                messages.error(request,str(e))
                return redirect('pagamentos:meus_pedidos')
            
            except Exception as e:
                messages.error(request,'Erro de comunicação ao cancelar pedido. Tente novamente mais tarde.')
                return redirect('pagamentos:meus_pedidos')
        
        else:
            messages.error(request,'Esse pedido não pode ser cancelado no momento.')
            
        return redirect('pagamentos:meus_pedidos')
    
    
    
class RefundedSolicitationAprovedView(View):
    def post(self,request,pedido_id):
        if not request.user.is_authenticated:
            return redirect('cadastro_login:login')
        
        pedido=get_object_or_404(Pedido,id=pedido_id,usuario=request.user)
        
        status_solicitacao=Solicitacao_reembolso.objects.filter(pedido=pedido).first()
        
        if status_solicitacao and pedido.pode_solicitar_reembolso:
            try:
                servico=CheckoutService()
                servico.solicitacao_reembolso(pedido,status_solicitacao)
                messages.success(request,'Reembolso solicitado e processado com sucesso.')
                
                obj=EmailForUser()
                obj.enviar_email_status_reembolso(status_solicitacao,pedido.pk)
                return redirect('pagamentos:meus_pedidos')
            except ValueError as e:
                messages.error(request,str(e))
                return redirect('pagamentos:meus_pedidos')
            except Exception as e:
                messages.error(request,'Erro de comunicação ao iniciar reembolso. Tente novamente.')
                return redirect('pagamentos:meus_pedidos')
            
        else:
            messages.error(request,'Esse pedido não pode ser reembolsado no momento.')
            
        return redirect('pagamentos:meus_pedidos')
                           
                           
@method_decorator(csrf_exempt,name='dispatch')                           
class PagseguroNotificationView(View):
    def post(self,request):
        
        body_utf8=request.body.decode('utf-8',errors='ignore')
        
        
        if not body_utf8:
            return HttpResponse('OK')
        
        order_id=None
        
        try:
            payload=json.loads(request.body)
            order_id=payload.get('id')
            
        except json.JSONDecodeError:
            if 'noticationCode' in request.POST:
                return HttpResponse('OK')
            else:
                return HttpResponse('OK')
            
            
        if not order_id:
            return HttpResponse('OK')
        
        try:
            servico=CheckoutService()
            servico.atualiza_status_notificacao(order_id)
            return HttpResponse('OK', status=200)
        except ValueError as e:
            logger.error(f'Aviso ao processar notificação {order_id}:{e}')
        except Exception as e:
            logger.error(f'Erro grave ao processar notificação {order_id}:{e}')
            
        return HttpResponse('OK', status=200)
        
        
                